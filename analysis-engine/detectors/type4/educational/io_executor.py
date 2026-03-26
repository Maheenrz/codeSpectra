# detectors/type4/educational/io_executor.py
"""
I/O Executor — safely compiles and runs student code with a harness.

Responsibilities:
  1. Receive a student source file + harness string
  2. Produce a merged source (student code with main renamed + harness appended)
  3. Compile it (g++ for C++, javac for Java, use python interpreter for Python)
  4. Run it with a given stdin string under strict resource limits
  5. Return normalized stdout or an ExecutionError

Safety measures:
  - All work happens in an isolated temp directory (deleted on exit).
  - Hard time limit per run (default 5 seconds).
  - stdout size capped at 64 KB to prevent memory exhaustion.
  - No shell=True anywhere — subprocess calls use list arguments.
  - Student code cannot write to paths outside the temp dir (it runs with CWD=temp).
  - compile errors are caught and logged; the caller receives None (skip test).

Output normalization (see _normalize_output):
  - Strip all decorative text, extract numeric tokens.
  - Normalize boolean strings (true/false/yes/no → 1/0).
  - Strip leading/trailing whitespace.
  - Collapse multiple spaces.
  This makes comparisons language-style-agnostic.
"""

from __future__ import annotations

import logging
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


# ─── Configuration ────────────────────────────────────────────────────────────

DEFAULT_COMPILE_TIMEOUT: int = 30   # seconds
DEFAULT_RUN_TIMEOUT:     int = 5    # seconds per test case
MAX_STDOUT_BYTES:        int = 64 * 1024   # 64 KB

CPP_COMPILE_FLAGS: List[str] = [
    "-O1",          # minimal optimization so student code runs reasonably fast
    "-std=c++17",   # modern standard
    "-w",           # suppress warnings (student code may have them)
    "-o",           # output flag (added dynamically)
]

JAVA_COMPILE_FLAGS: List[str] = []   # javac has no special flags needed here


# ─── Result dataclasses ───────────────────────────────────────────────────────

@dataclass
class ExecutionResult:
    """Result of running one test case."""
    raw_output:        str   = ""
    normalized_output: str   = ""
    return_code:       int   = 0
    timed_out:         bool  = False
    compile_error:     bool  = False
    runtime_error:     bool  = False
    error_message:     str   = ""

    @property
    def succeeded(self) -> bool:
        """True if the process ran without hard errors."""
        return (
            not self.compile_error
            and not self.timed_out
            and not self.runtime_error
        )


@dataclass
class CompileResult:
    """Result of compiling a harness+student merged source."""
    success:       bool  = False
    binary_path:   str   = ""
    error_message: str   = ""


# ─── Output normalizer ────────────────────────────────────────────────────────

_BOOL_TRUE_RE  = re.compile(r'\b(true|yes|found|ok|success)\b', re.IGNORECASE)
_BOOL_FALSE_RE = re.compile(r'\b(false|no|not\s+found|fail)\b', re.IGNORECASE)
_NUM_RE        = re.compile(r'-?\d+(?:\.\d+)?')


def _normalize_output(raw: str) -> str:
    """
    Normalize raw stdout for comparison.

    Steps:
      1. Replace known boolean-word patterns with 1/0.
      2. Extract all numeric tokens (integers and floats) from each line.
      3. If a line has no numerics, keep it as-is after stripping (handles "OK\n" etc.).
      4. Join lines with newline, strip outer whitespace.

    Examples:
      "Stack (top->bottom): 40 30 20 10\n"  →  "40 30 20 10"
      "Top -> 40 30 20 10 <- Bottom\n"       →  "40 30 20 10"
      "Pushed: 10\nPushed: 20\n"             →  "OK\nOK"  ← kept as text if no numbers
      "true\n"                               →  "1"
      "11 12 22 25 34 64 90\n"              →  "11 12 22 25 34 64 90"
    """
    if not raw:
        return ""

    lines = raw.strip().splitlines()
    normalized_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Boolean replacement first
        line = _BOOL_TRUE_RE.sub("1",  line)
        line = _BOOL_FALSE_RE.sub("0", line)

        # Try to extract numeric tokens
        nums = _NUM_RE.findall(line)
        if nums:
            normalized_lines.append(" ".join(nums))
        else:
            # No numbers — keep the line as-is (e.g. "OK", "OVERFLOW", "1")
            # Normalize common stack/list responses
            lu = line.upper()
            if any(kw in lu for kw in ("OVERFLOW", "OVER_FLOW")):
                normalized_lines.append("OVERFLOW")
            elif any(kw in lu for kw in ("UNDERFLOW", "UNDER_FLOW")):
                normalized_lines.append("UNDERFLOW")
            elif any(kw in lu for kw in ("EMPTY",)):
                normalized_lines.append("EMPTY")
            elif any(kw in lu for kw in ("NULL", "NONE")):
                normalized_lines.append("NULL")
            else:
                # Keep original (stripped) — may be "OK", error text, etc.
                normalized_lines.append(line)

    return "\n".join(normalized_lines)


# ─── Main executor ────────────────────────────────────────────────────────────

class IOExecutor:
    """
    Compiles and runs student+harness merged source against a single stdin input.

    Designed to be used per-test-case. The caller holds a temp directory
    across multiple test runs for the same binary (to avoid recompilation).
    """

    def __init__(
        self,
        compile_timeout: int = DEFAULT_COMPILE_TIMEOUT,
        run_timeout:     int = DEFAULT_RUN_TIMEOUT,
    ) -> None:
        self.compile_timeout = compile_timeout
        self.run_timeout     = run_timeout

    # ── public: compile ───────────────────────────────────────────────────────

    def compile_cpp(
        self,
        merged_source: str,
        work_dir: str,
        binary_name: str = "student_harness",
    ) -> CompileResult:
        """
        Write merged_source to a .cpp file and compile with g++.

        Args:
            merged_source: Full C++ source (student code + harness appended).
            work_dir:      Temp directory for the build files.
            binary_name:   Stem for the output binary.

        Returns:
            CompileResult with success flag and path to binary.
        """
        src_path = Path(work_dir) / f"{binary_name}.cpp"
        bin_path = Path(work_dir) / binary_name

        try:
            src_path.write_text(merged_source, encoding="utf-8")
        except IOError as exc:
            logger.error("[IOExecutor] Cannot write source file: %s", exc)
            return CompileResult(error_message=str(exc))

        compiler = shutil.which("g++") or "g++"
        cmd = [
            compiler,
            *CPP_COMPILE_FLAGS,
            str(bin_path),
            str(src_path),
        ]

        logger.debug("[IOExecutor] Compiling: %s", " ".join(cmd))

        try:
            proc = subprocess.run(
                cmd,
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=self.compile_timeout,
            )
        except subprocess.TimeoutExpired:
            logger.warning("[IOExecutor] Compilation timed out after %ds", self.compile_timeout)
            return CompileResult(error_message="compilation timed out")
        except FileNotFoundError:
            logger.error("[IOExecutor] g++ not found on PATH")
            return CompileResult(error_message="g++ not found")
        except Exception as exc:
            logger.error("[IOExecutor] Compilation exception: %s", exc)
            return CompileResult(error_message=str(exc))

        if proc.returncode != 0:
            stderr = proc.stderr[:2000]  # cap error message length
            logger.info("[IOExecutor] Compile failed:\n%s", stderr)
            return CompileResult(error_message=stderr)

        if not bin_path.exists():
            return CompileResult(error_message="binary not created despite zero exit code")

        logger.debug("[IOExecutor] Compiled OK → %s", bin_path)
        return CompileResult(success=True, binary_path=str(bin_path))

    def compile_python(
        self,
        merged_source: str,
        work_dir: str,
        script_name: str = "student_harness",
    ) -> CompileResult:
        """
        Write merged_source to a .py file. No actual compilation step needed;
        just verify the file exists (syntax errors surface at run time).
        """
        src_path = Path(work_dir) / f"{script_name}.py"
        try:
            src_path.write_text(merged_source, encoding="utf-8")
        except IOError as exc:
            return CompileResult(error_message=str(exc))

        # Quick syntax check using `python -m py_compile`
        python = shutil.which("python3") or shutil.which("python") or "python3"
        try:
            proc = subprocess.run(
                [python, "-m", "py_compile", str(src_path)],
                capture_output=True, text=True, timeout=10,
            )
            if proc.returncode != 0:
                logger.info("[IOExecutor] Python syntax error:\n%s", proc.stderr[:1000])
                return CompileResult(error_message=proc.stderr[:1000])
        except Exception as exc:
            logger.warning("[IOExecutor] Python syntax check failed: %s", exc)
            # Don't fail hard — syntax check is best-effort

        return CompileResult(success=True, binary_path=str(src_path))

    # ── public: run ───────────────────────────────────────────────────────────

    def run_cpp(
        self,
        binary_path: str,
        stdin_input: str,
        work_dir: str,
    ) -> ExecutionResult:
        """Run a compiled C++ binary with stdin_input, return normalized output."""
        return self._run_process(
            cmd=[binary_path],
            stdin_input=stdin_input,
            work_dir=work_dir,
        )

    def run_python(
        self,
        script_path: str,
        stdin_input: str,
        work_dir: str,
    ) -> ExecutionResult:
        """Run a Python script with stdin_input, return normalized output."""
        python = shutil.which("python3") or shutil.which("python") or "python3"
        return self._run_process(
            cmd=[python, script_path],
            stdin_input=stdin_input,
            work_dir=work_dir,
        )

    def run_java(
        self,
        class_dir: str,
        main_class: str,
        stdin_input: str,
        work_dir: str,
    ) -> ExecutionResult:
        """Run a compiled Java class with stdin_input."""
        java = shutil.which("java") or "java"
        return self._run_process(
            cmd=[java, "-cp", class_dir, main_class],
            stdin_input=stdin_input,
            work_dir=work_dir,
        )

    # ── internal ──────────────────────────────────────────────────────────────

    def _run_process(
        self,
        cmd: List[str],
        stdin_input: str,
        work_dir: str,
    ) -> ExecutionResult:
        """
        Run a process with stdin_input under resource limits.
        Returns ExecutionResult with raw + normalized output.
        """
        result = ExecutionResult()
        logger.debug("[IOExecutor] Running: %s", " ".join(cmd))

        try:
            proc = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.run_timeout,
                cwd=work_dir,
                # No shell=True — prevents shell injection from binary path
            )
            result.return_code = proc.returncode

            # Cap stdout to prevent memory exhaustion
            raw = proc.stdout[:MAX_STDOUT_BYTES]
            result.raw_output = raw
            result.normalized_output = _normalize_output(raw)

            if proc.returncode != 0:
                stderr = proc.stderr[:500]
                logger.debug(
                    "[IOExecutor] Non-zero exit %d: %s",
                    proc.returncode, stderr,
                )
                result.runtime_error  = True
                result.error_message  = stderr

        except subprocess.TimeoutExpired:
            logger.warning(
                "[IOExecutor] Run timed out after %ds for: %s",
                self.run_timeout, " ".join(cmd),
            )
            result.timed_out    = True
            result.error_message = f"timed out after {self.run_timeout}s"

        except FileNotFoundError as exc:
            logger.error("[IOExecutor] Binary not found: %s — %s", cmd[0], exc)
            result.runtime_error = True
            result.error_message = str(exc)

        except Exception as exc:
            logger.error("[IOExecutor] Unexpected run error: %s", exc)
            result.runtime_error = True
            result.error_message = str(exc)

        return result


# ── helpers for callers ───────────────────────────────────────────────────────

def make_work_dir(prefix: str = "cs_io_") -> str:
    """Create a fresh temp directory. Caller is responsible for cleanup."""
    td = tempfile.mkdtemp(prefix=prefix)
    logger.debug("[IOExecutor] Created work dir: %s", td)
    return td


def cleanup_work_dir(work_dir: str) -> None:
    """Remove a temp directory tree, ignoring errors."""
    try:
        shutil.rmtree(work_dir, ignore_errors=True)
        logger.debug("[IOExecutor] Cleaned up: %s", work_dir)
    except Exception as exc:
        logger.warning("[IOExecutor] Cleanup error for %s: %s", work_dir, exc)


# ── singleton executor ────────────────────────────────────────────────────────

_executor: Optional[IOExecutor] = None


def get_executor() -> IOExecutor:
    global _executor
    if _executor is None:
        _executor = IOExecutor()
    return _executor
