"""
boilerplate_stripper.py
========================
Strips common boilerplate before any comparison so detectors don't
false-positive on standard headers, includes, and template code.

Applied at file-read time in analyzer.py — original files are never modified.
"""
from __future__ import annotations
import re
from pathlib import Path

# ── Language → boilerplate patterns to strip ─────────────────────────────────

_CPP_STRIP = re.compile(
    r'^\s*#\s*include\s*[<"][^>"]+[>"]\s*$'   # #include <...> / "..."
    r'|^\s*#\s*pragma\s+once\s*$'              # #pragma once
    r'|^\s*using\s+namespace\s+std\s*;\s*$'    # using namespace std;
    r'|^\s*#\s*ifndef\s+\w+\s*$'              # include guards
    r'|^\s*#\s*define\s+\w+\s*$'
    r'|^\s*#\s*endif\s*.*$',
    re.MULTILINE,
)

_JAVA_STRIP = re.compile(
    r'^\s*import\s+[\w.*]+\s*;\s*$'            # import statements
    r'|^\s*package\s+[\w.]+\s*;\s*$',          # package declaration
    re.MULTILINE,
)

_PYTHON_STRIP = re.compile(
    r'^\s*import\s+\w[\w.]*\s*$'               # import x
    r'|^\s*from\s+\w[\w.]*\s+import\s+.*$'     # from x import y
    r'|^\s*#.*$',                               # comments
    re.MULTILINE,
)

_JS_STRIP = re.compile(
    r"""^\s*(?:import|export)\s+.*?['"][^'"]+['"]\s*;?\s*$""",  # import/export
    re.MULTILINE,
)

_EXT_MAP = {
    '.cpp': _CPP_STRIP, '.cc': _CPP_STRIP, '.cxx': _CPP_STRIP,
    '.c':   _CPP_STRIP, '.h':  _CPP_STRIP, '.hpp': _CPP_STRIP,
    '.java': _JAVA_STRIP,
    '.py':   _PYTHON_STRIP,
    '.js':   _JS_STRIP, '.jsx': _JS_STRIP,
    '.ts':   _JS_STRIP, '.tsx': _JS_STRIP,
}

# Minimum meaningful lines after stripping before we give up and return original
_MIN_LINES = 3


def strip_boilerplate(source: str, ext: str) -> str:
    """
    Remove boilerplate from source code.
    Returns the stripped source, or the original if stripping leaves too little.
    """
    pattern = _EXT_MAP.get(ext.lower())
    if pattern is None:
        return source

    stripped = pattern.sub('', source)

    # Remove blank lines produced by stripping
    lines = [l for l in stripped.splitlines() if l.strip()]
    if len(lines) < _MIN_LINES:
        return source  # too little left — keep original

    return '\n'.join(lines)


def strip_file(path: str | Path) -> str:
    """
    Read a file and return its boilerplate-stripped content.
    Falls back to raw content on any read error.
    """
    path = Path(path)
    try:
        source = path.read_text(encoding='utf-8', errors='ignore')
        return strip_boilerplate(source, path.suffix)
    except Exception:
        return ''
