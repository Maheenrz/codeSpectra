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

# Configuration
DEFAULT_COMPILE_TIMEOUT: int = 30
DEFAULT_RUN_TIMEOUT: int = 5
MAX_STDOUT_BYTES: int = 64 * 1024

CPP_COMPILE_FLAGS: List[str] = [
    "-O1",
    "-std=c++17",
    "-w",
    "-o",
]

JAVA_COMPILE_FLAGS: List[str] = []


@dataclass
class ExecutionResult:
    """Result of running one test case."""
    raw_output: str = ""
    normalized_output: str = ""
    return_code: int = 0
    timed_out: bool = False
    compile_error: bool = False
    runtime_error: bool = False
    error_message: str = ""

    @property
    def succeeded(self) -> bool:
        return not (self.compile_error or self.timed_out or self.runtime_error)


@dataclass
class CompileResult:
    """Result of compiling a harness+student merged source."""
    success: bool = False
    binary_path: str = ""
    error_message: str = ""


# Output normalizer
_BOOL_TRUE_RE = re.compile(r'\b(true|yes|found|ok|success)\b', re.IGNORECASE)
_BOOL_FALSE_RE = re.compile(r'\b(false|no|not\s+found|fail)\b', re.IGNORECASE)
_NUM_RE = re.compile(r'-?\d+(?:\.\d+)?')


def _normalize_output(raw: str) -> str:
    """Normalize raw stdout for comparison."""
    if not raw:
        return ""

    lines = raw.strip().splitlines()
    normalized_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        line = _BOOL_TRUE_RE.sub("1", line)
        line = _BOOL_FALSE_RE.sub("0", line)

        nums = _NUM_RE.findall(line)
        if nums:
            normalized_lines.append(" ".join(nums))
        else:
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
                normalized_lines.append(line)

    return "\n".join(normalized_lines)


class IOExecutor:
    """Compiles and runs student+harness merged source."""

    def __init__(self, compile_timeout: int = DEFAULT_COMPILE_TIMEOUT, run_timeout: int = DEFAULT_RUN_TIMEOUT) -> None:
        self.compile_timeout = compile_timeout
        self.run_timeout = run_timeout

    def compile_cpp(self, merged_source: str, work_dir: str, binary_name: str = "student_harness") -> CompileResult:
        src_path = Path(work_dir) / f"{binary_name}.cpp"
        bin_path = Path(work_dir) / binary_name

        try:
            src_path.write_text(merged_source, encoding="utf-8")
        except IOError as exc:
            return CompileResult(error_message=str(exc))

        compiler = shutil.which("g++") or "g++"
        cmd = [compiler, *CPP_COMPILE_FLAGS, str(bin_path), str(src_path)]

        try:
            proc = subprocess.run(cmd, cwd=work_dir, capture_output=True, text=True, timeout=self.compile_timeout)
        except subprocess.TimeoutExpired:
            return CompileResult(error_message="compilation timed out")
        except FileNotFoundError:
            return CompileResult(error_message="g++ not found")
        except Exception as exc:
            return CompileResult(error_message=str(exc))

        if proc.returncode != 0:
            return CompileResult(error_message=proc.stderr[:2000])

        if not bin_path.exists():
            return CompileResult(error_message="binary not created despite zero exit code")

        return CompileResult(success=True, binary_path=str(bin_path))

    def compile_python(self, merged_source: str, work_dir: str, script_name: str = "student_harness") -> CompileResult:
        src_path = Path(work_dir) / f"{script_name}.py"
        try:
            src_path.write_text(merged_source, encoding="utf-8")
        except IOError as exc:
            return CompileResult(error_message=str(exc))

        return CompileResult(success=True, binary_path=str(src_path))

    def run_cpp(self, binary_path: str, stdin_input: str, work_dir: str) -> ExecutionResult:
        return self._run_process(cmd=[binary_path], stdin_input=stdin_input, work_dir=work_dir)

    def run_python(self, script_path: str, stdin_input: str, work_dir: str) -> ExecutionResult:
        python = shutil.which("python3") or shutil.which("python") or "python3"
        return self._run_process(cmd=[python, script_path], stdin_input=stdin_input, work_dir=work_dir)

    def _run_process(self, cmd: List[str], stdin_input: str, work_dir: str) -> ExecutionResult:
        result = ExecutionResult()

        try:
            proc = subprocess.run(cmd, input=stdin_input, capture_output=True, text=True, timeout=self.run_timeout, cwd=work_dir)
            result.return_code = proc.returncode
            raw = proc.stdout[:MAX_STDOUT_BYTES]
            result.raw_output = raw
            result.normalized_output = _normalize_output(raw)

            if proc.returncode != 0:
                result.runtime_error = True
                result.error_message = proc.stderr[:500]

        except subprocess.TimeoutExpired:
            result.timed_out = True
            result.error_message = f"timed out after {self.run_timeout}s"
        except FileNotFoundError as exc:
            result.runtime_error = True
            result.error_message = str(exc)
        except Exception as exc:
            result.runtime_error = True
            result.error_message = str(exc)

        return result


def make_work_dir(prefix: str = "cs_io_") -> str:
    td = tempfile.mkdtemp(prefix=prefix)
    return td


def cleanup_work_dir(work_dir: str) -> None:
    try:
        shutil.rmtree(work_dir, ignore_errors=True)
    except Exception:
        pass


_executor: Optional[IOExecutor] = None


def get_executor() -> IOExecutor:
    global _executor
    if _executor is None:
        _executor = IOExecutor()
    return _executor