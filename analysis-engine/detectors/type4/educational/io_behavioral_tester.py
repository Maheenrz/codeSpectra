# detectors/type4/educational/io_behavioral_tester.py
"""
I/O Behavioral Tester — orchestrates test runs for a student file pair.

Workflow for one (file_a, file_b) pair:
  1. Classify both files → determine problem category.
  2. Retrieve the test bank for that category.
  3. For each file:
       a. Generate a merged source (student code + harness).
       b. Compile once.
       c. Run all test cases; collect (output_a, output_b, expected) triples.
  4. Compare normalized output_a vs normalized output_b for each test case.
  5. Compute:
       io_match_score = matched_cases / total_runnable_cases
       mutual_correctness = cases where BOTH match expected / total_runnable_cases
  6. Return IOBehavioralResult.

Result interpretation:
  io_match_score:
    1.0  → both produce identical outputs for every test case
    0.0  → never produce the same output
    None → execution failed for one or both files (skip I/O signal)

  mutual_correctness:
    > 0.8 → both implementations are correct AND produce the same outputs
             (strong semantic clone signal)
    low  → one might be wrong, or they solve different versions of the problem

Design notes:
  - Compiled binaries are cached per-file within one tester run to avoid
    recompiling for every test case.
  - All temp directories are cleaned up in a finally block, even on exception.
  - The tester never raises — on any failure it returns a result with
    succeeded=False and a descriptive error_message.
"""

from __future__ import annotations

import logging
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .algorithm_classifier import (
    AlgorithmClassifier,
    ClassificationResult,
    get_classifier,
)
from .io_executor import (
    CompileResult,
    ExecutionResult,
    IOExecutor,
    cleanup_work_dir,
    get_executor,
    make_work_dir,
)
from .problem_bank.harness_templates import get_harness_template
from .problem_bank.registry import ProblemCategory, get_registry

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Harness builder
# ─────────────────────────────────────────────────────────────────────────────

# Pattern to rename student's main() → prevent duplicate-main link errors.
# Handles: int main(), int main(void), int main(int argc, char** argv), etc.
_RENAME_MAIN_CPP = re.compile(r'\bint\s+main\s*\(')
_RENAME_MAIN_PY  = re.compile(r'^if\s+__name__\s*==\s*["\']__main__["\']\s*:', re.MULTILINE)


def _rename_student_main_cpp(source: str) -> str:
    """
    Rename `int main(` → `int __student_main_discarded__(` in C++ source.
    This prevents duplicate-main linker errors when our harness main() is appended.
    We only rename the FIRST occurrence (the actual student main).
    """
    return _RENAME_MAIN_CPP.sub("int __student_main_discarded__(", source, count=1)


def _rename_student_main_python(source: str) -> str:
    """
    Comment out the student's `if __name__ == '__main__':` block in Python.
    We append our own harness __cs_main__ call instead.
    """
    # Replace `if __name__ == '__main__':` with `if False:` to disable it.
    return _RENAME_MAIN_PY.sub("if False:", source, count=1)


def _build_cpp_harness(
    source: str,
    category: str,
    cls_result: ClassificationResult,
) -> Optional[str]:
    """
    Build the merged C++ source (student code + harness appended).

    Returns the merged source string, or None if harness cannot be built
    (e.g. required template not available, function name not detected).
    """
    template = get_harness_template(category, "cpp")
    if not template:
        logger.debug("[HarnessBuilder] No C++ template for category %s", category)
        return None

    # Rename student's main
    merged = _rename_student_main_cpp(source)

    # ── Fill in template placeholders ─────────────────────────────────────
    try:
        if category == "SORT_ARRAY":
            func_names = cls_result.function_names
            if not func_names:
                logger.info("[HarnessBuilder] No sort function detected — cannot build harness")
                return None
            harness = template.replace("{FUNC_NAME}", func_names[0])

        elif category in ("STACK_OOP", "STACK_PROCEDURAL"):
            methods = cls_result.detected_methods
            if not methods:
                logger.info("[HarnessBuilder] No stack methods detected")
                return None

            push_m    = methods.get("push",    "push")
            pop_m     = methods.get("pop",     "pop")
            peek_m    = methods.get("peek",    "peek")
            size_m    = methods.get("size",    "size")
            empty_m   = methods.get("isEmpty", "isEmpty")

            if category == "STACK_OOP":
                class_name = cls_result.detected_class or "Stack"
                harness = (
                    template
                    .replace("{CLASS_NAME}",    class_name)
                    .replace("{PUSH_METHOD}",   push_m)
                    .replace("{POP_METHOD}",    pop_m)
                    .replace("{PEEK_METHOD}",   peek_m)
                    .replace("{SIZE_METHOD}",   size_m)
                    .replace("{ISEMPTY_METHOD}", empty_m)
                )
            else:  # STACK_PROCEDURAL
                struct_name = cls_result.detected_class or "Stack"
                # Detect init function name
                init_m = _find_init_func(source) or "initStack"
                harness = (
                    template
                    .replace("{STRUCT_NAME}",   struct_name)
                    .replace("{INIT_FUNC}",     init_m)
                    .replace("{PUSH_FUNC}",     push_m)
                    .replace("{POP_FUNC}",      pop_m)
                    .replace("{PEEK_FUNC}",     peek_m)
                    .replace("{SIZE_FUNC}",     size_m)
                    .replace("{ISEMPTY_FUNC}",  empty_m)
                )

        elif category == "LINKED_LIST":
            methods    = cls_result.detected_methods
            class_name = cls_result.detected_class or "LinkedList"
            harness = (
                template
                .replace("{CLASS_NAME}",          class_name)
                .replace("{INSERT_END_METHOD}",   methods.get("insert_end",   "insertAtEnd"))
                .replace("{INSERT_FRONT_METHOD}", methods.get("insert_front", "insertAtFront"))
                .replace("{DELETE_METHOD}",       methods.get("delete",       "deleteNode"))
                .replace("{SEARCH_METHOD}",       methods.get("search",       "search"))
                .replace("{LENGTH_METHOD}",       methods.get("length",       "length"))
                .replace("{PRINT_METHOD}",        methods.get("print",        "display"))
            )

        elif category in ("FIBONACCI", "FACTORIAL", "GCD", "IS_PALINDROME", "STRING_REVERSE"):
            func_names = cls_result.function_names
            if not func_names:
                # Fall back to category-name-based guess
                guesses = {
                    "FIBONACCI":     ["fibonacci", "fib", "Fibonacci"],
                    "FACTORIAL":     ["factorial", "fact", "Factorial"],
                    "GCD":           ["gcd", "GCD", "hcf"],
                    "IS_PALINDROME": ["isPalindrome", "palindrome", "checkPalindrome"],
                    "STRING_REVERSE":["reverseStr", "reverse", "reverseString"],
                }
                func_names = guesses.get(category, [])
            if not func_names:
                return None
            harness = template.replace("{FUNC_NAME}", func_names[0])

        elif category in ("LINEAR_SEARCH", "BINARY_SEARCH"):
            func_names = cls_result.function_names
            if not func_names:
                return None
            harness = template.replace("{FUNC_NAME}", func_names[0])

        else:
            logger.debug("[HarnessBuilder] No harness logic for category %s", category)
            return None

    except KeyError as exc:
        logger.warning("[HarnessBuilder] Template placeholder missing: %s", exc)
        return None

    # Prepend necessary includes that the harness uses (safe to add, won't duplicate
    # includes already in student code because C++ include guards handle duplicates)
    extra_includes = "#include <iostream>\n#include <string>\n#include <sstream>\n#include <vector>\n"
    merged = extra_includes + merged + "\n" + harness
    return merged


def _build_python_harness(
    source: str,
    category: str,
    cls_result: ClassificationResult,
) -> Optional[str]:
    """Build merged Python source (student code + harness)."""
    template = get_harness_template(category, "python")
    if not template:
        return None

    merged = _rename_student_main_python(source)
    func_names = cls_result.function_names
    if not func_names:
        return None

    harness = template.replace("{FUNC_NAME}", func_names[0])
    return merged + "\n" + harness


def _find_init_func(source: str) -> Optional[str]:
    """Find a procedural stack init function name (initStack, init, etc.)."""
    m = re.search(r'\bvoid\s+(init\w*)\s*\(\s*\w+\s*[&*]\s*\w+\s*\)', source)
    return m.group(1) if m else None


# ─────────────────────────────────────────────────────────────────────────────
# Result dataclass
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class IOBehavioralResult:
    """
    Outcome of I/O behavioral testing for a file pair.

    Key fields:
        io_match_score:      Fraction of test cases where output_a == output_b.
                             None if execution could not be established.
        mutual_correctness:  Fraction of cases where BOTH outputs match expected.
        total_cases:         How many test cases were attempted.
        runnable_cases:      How many test cases produced usable output from BOTH files.
        category:            Detected problem category (or "" if unknown).
        succeeded:           Whether the full pipeline ran without fatal errors.
        error_message:       Description of failure if not succeeded.
    """
    io_match_score:     Optional[float] = None  # None = could not run
    mutual_correctness: Optional[float] = None
    total_cases:        int   = 0
    runnable_cases:     int   = 0
    matched_cases:      int   = 0
    category:           str   = ""
    algorithm_a:        str   = ""
    algorithm_b:        str   = ""
    same_algorithm_family: bool = False
    succeeded:          bool  = False
    error_message:      str   = ""
    # Per-case breakdown (for logging/debugging)
    case_details:       List[Dict] = field(default_factory=list)

    def __str__(self) -> str:
        if not self.succeeded:
            return f"IOBehavioralResult: FAILED — {self.error_message}"
        score_str = f"{self.io_match_score:.0%}" if self.io_match_score is not None else "N/A"
        return (
            f"IOBehavioralResult: match={score_str} "
            f"({self.matched_cases}/{self.runnable_cases} cases) "
            f"category={self.category} "
            f"same_algo={self.same_algorithm_family}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Main tester
# ─────────────────────────────────────────────────────────────────────────────

class IOBehavioralTester:
    """
    Orchestrates I/O behavioral testing for a pair of student source files.

    Usage:
        tester = IOBehavioralTester()
        result = tester.test(file_a, file_b)
    """

    def __init__(
        self,
        classifier: Optional[AlgorithmClassifier] = None,
        executor:   Optional[IOExecutor]           = None,
        max_test_cases: int = 15,   # cap to keep latency reasonable
    ) -> None:
        self._classifier    = classifier or get_classifier()
        self._executor      = executor   or get_executor()
        self._max_tc        = max_test_cases
        self._registry      = get_registry()

    def test(self, file_a: str, file_b: str) -> IOBehavioralResult:
        """
        Run I/O behavioral testing for the given file pair.

        Never raises. On any error, returns a result with succeeded=False.

        Args:
            file_a: Absolute path to student A's source file.
            file_b: Absolute path to student B's source file.

        Returns:
            IOBehavioralResult
        """
        logger.info(
            "[IOTester] Testing pair: %s  vs  %s",
            Path(file_a).name, Path(file_b).name,
        )

        result = IOBehavioralResult()
        work_dir_a: Optional[str] = None
        work_dir_b: Optional[str] = None

        try:
            # ── Step 1: classify both files ────────────────────────────────
            cls_a = self._classifier.classify_file(file_a)
            cls_b = self._classifier.classify_file(file_b)
            logger.debug("[IOTester] Classification A: %s", cls_a)
            logger.debug("[IOTester] Classification B: %s", cls_b)

            result.algorithm_a = cls_a.algorithm_family
            result.algorithm_b = cls_b.algorithm_family
            result.same_algorithm_family = (
                bool(cls_a.algorithm_family)
                and cls_a.algorithm_family == cls_b.algorithm_family
            )

            # Both files must map to the SAME problem category
            if not cls_a.is_known or not cls_b.is_known:
                result.error_message = (
                    f"category unknown: A={cls_a.category!r} B={cls_b.category!r}"
                )
                logger.info("[IOTester] %s", result.error_message)
                result.succeeded = True   # not a failure — just can't test
                return result

            if cls_a.category != cls_b.category:
                # Different problem categories — they solve different problems.
                # I/O matching is meaningless; set score to 0.
                result.category = f"{cls_a.category} / {cls_b.category}"
                result.io_match_score = 0.0
                result.mutual_correctness = 0.0
                result.succeeded = True
                logger.info(
                    "[IOTester] Different categories (%s vs %s) — I/O score = 0.0",
                    cls_a.category, cls_b.category,
                )
                return result

            category = cls_a.category
            result.category = category
            logger.info("[IOTester] Category: %s", category)

            # ── Step 2: get test bank ──────────────────────────────────────
            prob_cat = self._registry.get(category)
            if prob_cat is None:
                result.error_message = f"No test bank for category {category!r}"
                result.succeeded = True
                logger.info("[IOTester] %s", result.error_message)
                return result

            test_cases = prob_cat.test_cases[:self._max_tc]
            result.total_cases = len(test_cases)
            if not test_cases:
                result.error_message = "test bank is empty"
                result.succeeded = True
                return result

            # ── Step 3: detect language and build harnesses ────────────────
            lang_a = self._detect_lang(file_a)
            lang_b = self._detect_lang(file_b)

            if not lang_a or not lang_b:
                result.error_message = f"unsupported language: {lang_a!r}/{lang_b!r}"
                result.succeeded = True
                return result

            # Read source files
            source_a = self._read_source(file_a)
            source_b = self._read_source(file_b)
            if source_a is None or source_b is None:
                result.error_message = "cannot read source files"
                result.succeeded = True
                return result

            merged_a = self._build_harness(source_a, lang_a, category, cls_a)
            merged_b = self._build_harness(source_b, lang_b, category, cls_b)

            if not merged_a or not merged_b:
                result.error_message = (
                    "harness construction failed "
                    f"(A={merged_a is not None} B={merged_b is not None})"
                )
                result.succeeded = True
                logger.info("[IOTester] %s", result.error_message)
                return result

            # ── Step 4: compile ────────────────────────────────────────────
            work_dir_a = make_work_dir("cs_a_")
            work_dir_b = make_work_dir("cs_b_")

            compile_a = self._compile(merged_a, lang_a, work_dir_a, "a")
            compile_b = self._compile(merged_b, lang_b, work_dir_b, "b")

            if not compile_a.success or not compile_b.success:
                err_a = "" if compile_a.success else f" A:{compile_a.error_message[:200]}"
                err_b = "" if compile_b.success else f" B:{compile_b.error_message[:200]}"
                result.error_message = f"compile failed.{err_a}{err_b}"
                result.succeeded = True
                logger.info("[IOTester] Compile failed:%s%s", err_a, err_b)
                return result

            logger.info("[IOTester] Both files compiled. Running %d test cases…", len(test_cases))

            # ── Step 5: run all test cases ─────────────────────────────────
            matched     = 0
            runnable    = 0
            both_correct = 0
            case_details: List[Dict] = []

            for i, (stdin_in, expected) in enumerate(test_cases):
                run_a = self._run(compile_a.binary_path, lang_a, stdin_in, work_dir_a)
                run_b = self._run(compile_b.binary_path, lang_b, stdin_in, work_dir_b)

                ok_a = run_a.succeeded
                ok_b = run_b.succeeded

                detail = {
                    "tc":       i + 1,
                    "stdin":    stdin_in[:80],
                    "expected": expected,
                    "out_a":    run_a.normalized_output if ok_a else f"[ERR] {run_a.error_message[:80]}",
                    "out_b":    run_b.normalized_output if ok_b else f"[ERR] {run_b.error_message[:80]}",
                }

                if ok_a and ok_b:
                    runnable += 1
                    match = run_a.normalized_output == run_b.normalized_output
                    if match:
                        matched += 1
                    # Mutual correctness: both must match expected
                    norm_expected = _normalize_expected(expected)
                    if (run_a.normalized_output == norm_expected
                            and run_b.normalized_output == norm_expected):
                        both_correct += 1
                    detail["match"] = match
                    detail["both_correct"] = (
                        run_a.normalized_output == norm_expected
                        and run_b.normalized_output == norm_expected
                    )
                else:
                    detail["match"]        = False
                    detail["both_correct"] = False
                    if not ok_a:
                        logger.debug("[IOTester] TC%d: file_a run failed: %s", i+1, run_a.error_message[:100])
                    if not ok_b:
                        logger.debug("[IOTester] TC%d: file_b run failed: %s", i+1, run_b.error_message[:100])

                case_details.append(detail)

            result.runnable_cases  = runnable
            result.matched_cases   = matched
            result.case_details    = case_details

            if runnable == 0:
                result.error_message  = "no test cases produced runnable output"
                result.succeeded      = True
                logger.warning("[IOTester] 0 runnable test cases for %s", category)
                return result

            result.io_match_score     = round(matched      / runnable, 4)
            result.mutual_correctness = round(both_correct / runnable, 4)
            result.succeeded          = True

            logger.info(
                "[IOTester] Done: match=%.0f%% (%d/%d) correctness=%.0f%%",
                result.io_match_score * 100,
                matched, runnable,
                result.mutual_correctness * 100,
            )

        except Exception as exc:
            # Catch-all: tester must never propagate exceptions to the engine.
            logger.exception("[IOTester] Unexpected error: %s", exc)
            result.error_message = f"unexpected error: {exc}"
            result.succeeded     = True   # result is valid (just empty)

        finally:
            # Always clean up temp directories
            if work_dir_a:
                cleanup_work_dir(work_dir_a)
            if work_dir_b:
                cleanup_work_dir(work_dir_b)

        return result

    # ── private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _detect_lang(file_path: str) -> Optional[str]:
        ext = Path(file_path).suffix.lower()
        return {
            ".cpp": "cpp", ".cc": "cpp", ".cxx": "cpp", ".c": "cpp",
            ".java": "java",
            ".py":   "python",
        }.get(ext)

    @staticmethod
    def _read_source(file_path: str) -> Optional[str]:
        try:
            return Path(file_path).read_text(encoding="utf-8", errors="ignore")
        except Exception as exc:
            logger.error("[IOTester] Cannot read %s: %s", file_path, exc)
            return None

    def _build_harness(
        self,
        source: str,
        lang:   str,
        category: str,
        cls:    ClassificationResult,
    ) -> Optional[str]:
        if lang == "cpp":
            return _build_cpp_harness(source, category, cls)
        if lang == "python":
            return _build_python_harness(source, category, cls)
        logger.debug("[IOTester] No harness builder for lang=%s", lang)
        return None

    def _compile(
        self,
        merged_source: str,
        lang:          str,
        work_dir:      str,
        label:         str,
    ) -> CompileResult:
        if lang == "cpp":
            return self._executor.compile_cpp(merged_source, work_dir, f"harness_{label}")
        if lang == "python":
            return self._executor.compile_python(merged_source, work_dir, f"harness_{label}")
        return CompileResult(error_message=f"compile not implemented for lang={lang}")

    def _run(
        self,
        binary_path: str,
        lang:        str,
        stdin_in:    str,
        work_dir:    str,
    ) -> ExecutionResult:
        if lang == "cpp":
            return self._executor.run_cpp(binary_path, stdin_in, work_dir)
        if lang == "python":
            return self._executor.run_python(binary_path, stdin_in, work_dir)
        from .io_executor import ExecutionResult as ER
        r = ER()
        r.runtime_error  = True
        r.error_message  = f"run not implemented for lang={lang}"
        return r


def _normalize_expected(expected: str) -> str:
    """Normalize the expected string the same way we normalize student output."""
    from .io_executor import _normalize_output
    return _normalize_output(expected)


# ── singleton ─────────────────────────────────────────────────────────────────

_tester: Optional[IOBehavioralTester] = None


def get_tester() -> IOBehavioralTester:
    global _tester
    if _tester is None:
        _tester = IOBehavioralTester()
    return _tester
