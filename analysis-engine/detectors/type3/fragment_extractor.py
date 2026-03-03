"""
Fragment Extractor — NiCad Step 1
==================================
Extracts function/method/block fragments from source files using
regex-based parsing (no tree-sitter dependency).

A fragment is a contiguous block of code (a function, method, or
meaningful block) with:
  - min_lines: minimum source lines (default 6, like NiCad)
  - min_tokens: minimum token count (default 20)

Supports: C/C++, Java, Python, JavaScript/TypeScript
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class Fragment:
    """A single code fragment extracted from a file."""
    file_path:    str
    name:         str          # function/method name or "block_N"
    start_line:   int
    end_line:     int
    source_lines: List[str]    # raw lines
    tokens:       List[str]    # tokenized (raw)

    @property
    def line_count(self) -> int:
        return self.end_line - self.start_line + 1

    @property
    def token_count(self) -> int:
        return len(self.tokens)


# ── Language patterns ─────────────────────────────────────────────────────────

# C++ / C / Java  — matches "type name(...) {" with brace tracking
_CPP_JAVA_FUNC = re.compile(
    r'^[ \t]*(?:(?:public|private|protected|static|virtual|inline|override|'
    r'const|explicit|friend|extern|async|synchronized|abstract|final)\s+)*'
    r'[\w:<>*&\[\]]+\s+(\w+)\s*\([^;]*\)\s*(?:const\s*)?(?:noexcept\s*)?'
    r'(?:override\s*)?(?:->\s*[\w:<>*&\[\]]+\s*)?\{',
    re.MULTILINE
)

# Python — def or async def
_PYTHON_FUNC = re.compile(
    r'^([ \t]*)(async\s+)?def\s+(\w+)\s*\(', re.MULTILINE
)

# JavaScript / TypeScript — function / arrow / class method
_JS_FUNC = re.compile(
    r'^[ \t]*(?:(?:async|static|public|private|protected|export|default)\s+)*'
    r'(?:function\s+(\w+)|(\w+)\s*[:=]\s*(?:async\s*)?\(|(\w+)\s*\()',
    re.MULTILINE
)

_EXT_LANG = {
    ".cpp": "cpp", ".c": "cpp", ".h": "cpp",
    ".hpp": "cpp", ".cc": "cpp", ".cxx": "cpp",
    ".java": "java",
    ".py": "python",
    ".js": "javascript", ".ts": "javascript",
    ".jsx": "javascript", ".tsx": "javascript",
}


class FragmentExtractor:
    def __init__(self, min_lines: int = 6, min_tokens: int = 20):
        self.min_lines  = min_lines
        self.min_tokens = min_tokens

    # ── Public API ────────────────────────────────────────────────────────────

    def extract(self, file_path: str) -> List[Fragment]:
        """Extract all fragments from a source file."""
        path = Path(file_path)
        if not path.exists():
            return []
        lang = _EXT_LANG.get(path.suffix.lower(), "cpp")
        try:
            source = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return []

        if lang == "python":
            fragments = self._extract_python(source, file_path)
        else:
            fragments = self._extract_braced(source, file_path, lang)

        # Filter by size
        return [f for f in fragments
                if f.line_count >= self.min_lines
                and f.token_count >= self.min_tokens]

    def extract_many(self, file_paths: List[str]) -> List[Fragment]:
        """Extract fragments from multiple files."""
        result = []
        for fp in file_paths:
            result.extend(self.extract(fp))
        return result

    # ── C++ / Java / JS: brace-tracking ──────────────────────────────────────

    def _extract_braced(self, source: str, file_path: str,
                        lang: str) -> List[Fragment]:
        lines = source.splitlines()
        fragments: List[Fragment] = []
        used_starts: set = set()

        pattern = _CPP_JAVA_FUNC if lang in ("cpp", "java") else _JS_FUNC
        for m in pattern.finditer(source):
            # Find which line this match starts on
            start_line = source[:m.start()].count("\n")
            if start_line in used_starts:
                continue

            # Find opening brace on or near match line
            open_pos = source.find("{", m.start())
            if open_pos == -1:
                continue

            # Track braces to find the closing one
            depth = 0
            end_pos = open_pos
            for i in range(open_pos, len(source)):
                if source[i] == "{":
                    depth += 1
                elif source[i] == "}":
                    depth -= 1
                    if depth == 0:
                        end_pos = i
                        break

            end_line = source[:end_pos].count("\n")
            if end_line <= start_line:
                continue

            name_groups = [g for g in m.groups() if g]
            name = name_groups[0] if name_groups else f"block_{start_line}"

            frag_lines = lines[start_line: end_line + 1]
            tokens     = self._tokenize_lines(frag_lines)

            fragments.append(Fragment(
                file_path=file_path,
                name=name,
                start_line=start_line + 1,
                end_line=end_line + 1,
                source_lines=frag_lines,
                tokens=tokens,
            ))
            used_starts.add(start_line)

        return fragments

    # ── Python: indent-tracking ───────────────────────────────────────────────

    def _extract_python(self, source: str, file_path: str) -> List[Fragment]:
        lines  = source.splitlines()
        n      = len(lines)
        frags: List[Fragment] = []

        for m in _PYTHON_FUNC.finditer(source):
            start_line = source[:m.start()].count("\n")
            indent_str = m.group(1)
            base_indent = len(indent_str.expandtabs(4))
            name = m.group(3)

            end_line = start_line
            for i in range(start_line + 1, n):
                stripped = lines[i].lstrip()
                if not stripped:          # blank line — keep scanning
                    continue
                line_indent = len(lines[i].expandtabs(4)) - len(stripped)
                if line_indent <= base_indent:
                    break
                end_line = i

            frag_lines = lines[start_line: end_line + 1]
            tokens     = self._tokenize_lines(frag_lines)
            frags.append(Fragment(
                file_path=file_path,
                name=name,
                start_line=start_line + 1,
                end_line=end_line + 1,
                source_lines=frag_lines,
                tokens=tokens,
            ))

        return frags

    # ── Tokenizer (raw, for size check only) ─────────────────────────────────

    @staticmethod
    def _tokenize_lines(lines: List[str]) -> List[str]:
        tokens = []
        for line in lines:
            # Strip single-line comments
            line = re.sub(r'//.*$',  '',  line)
            line = re.sub(r'#.*$',   '',  line)
            tokens.extend(re.findall(r'[a-zA-Z_]\w*|[0-9]+(?:\.[0-9]+)?|[^\s\w]', line))
        return tokens