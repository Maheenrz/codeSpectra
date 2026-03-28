"""
Fragment Extractor — Code Block Extraction
============================================
Extracts function/method/block fragments from source files using
regex-based parsing (no tree-sitter dependency).
"""

from __future__ import annotations
import re
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

@dataclass
class Fragment:
    """A single code fragment extracted from a file."""
    file_path:    str
    name:         str
    start_line:   int
    end_line:     int
    source_lines: List[str]
    tokens:       List[str]
    student_id:   Optional[str] = None
    student_name: Optional[str] = None

    @property
    def line_count(self) -> int:
        return self.end_line - self.start_line + 1

    @property
    def token_count(self) -> int:
        return len(self.tokens)


# ── Language patterns ─────────────────────────────────────────────────────────

_CPP_JAVA_FUNC = re.compile(
    r'^[ \t]*(?:(?:public|private|protected|static|virtual|inline|override|'
    r'const|explicit|friend|extern|async|synchronized|abstract|final)\s+)*'
    r'[\w:<>*&\[\]]+\s+(\w+)\s*\([^;]*\)\s*(?:const\s*)?(?:noexcept\s*)?'
    r'(?:override\s*)?(?:->\s*[\w:<>*&\[\]]+\s*)?\{',
    re.MULTILINE
)

_PYTHON_FUNC = re.compile(
    r'^([ \t]*)(async\s+)?def\s+(\w+)\s*\(', re.MULTILINE
)

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
    def __init__(self, min_lines: int = 6, min_tokens: int = 20, exclude_headers: bool = True):
        self.min_lines = min_lines
        self.min_tokens = min_tokens
        self.exclude_headers = exclude_headers

    def extract(self, file_path: str) -> List[Fragment]:
        """Extract fragments, skipping header files and macOS files"""
        path = Path(file_path)
        if not path.exists():
            return []

        # 1. macOS files
        if self._is_macos_file(path):
            logger.debug(f"Skipping macOS file: {path.name}")
            return []

        # 2. Header files
        if self.exclude_headers and path.suffix.lower() in ['.h', '.hpp', '.hxx']:
            logger.debug(f"Skipping header file: {path.name}")
            return []

        # 3. Boilerplate files (main, driver, test, etc.)
        if self._is_boilerplate_file(path):
            logger.debug(f"Skipping boilerplate file: {path.name}")
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

    def _is_macos_file(self, path: Path) -> bool:
        """Skip macOS metadata files"""
        name = path.name
        if name.startswith('._') or '__MACOSX' in str(path):
            return True
        if name.startswith('.'):
            return True
        ignore_patterns = ['.DS_Store', 'Thumbs.db', 'desktop.ini']
        if name in ignore_patterns:
            return True
        return False

    def _is_boilerplate_file(self, path: Path) -> bool:
        boilerplate_patterns = ['test', 'unittest', 'spec', 'main', 'driver', 'example', 'demo']
        name = path.stem.lower()
        return any(pattern in name for pattern in boilerplate_patterns)

    def extract_many(self, file_paths: List[str]) -> List[Fragment]:
        result = []
        for fp in file_paths:
            result.extend(self.extract(fp))
        return result

    def _extract_braced(self, source: str, file_path: str, lang: str) -> List[Fragment]:
        lines = source.splitlines()
        fragments: List[Fragment] = []
        used_starts: set = set()

        pattern = _CPP_JAVA_FUNC if lang in ("cpp", "java") else _JS_FUNC
        for m in pattern.finditer(source):
            start_line = source[:m.start()].count("\n")
            if start_line in used_starts:
                continue

            open_pos = source.find("{", m.start())
            if open_pos == -1:
                continue

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
            tokens = self._tokenize_lines(frag_lines)

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

    def _extract_python(self, source: str, file_path: str) -> List[Fragment]:
        lines = source.splitlines()
        n = len(lines)
        frags: List[Fragment] = []

        for m in _PYTHON_FUNC.finditer(source):
            start_line = source[:m.start()].count("\n")
            indent_str = m.group(1)
            base_indent = len(indent_str.expandtabs(4))
            name = m.group(3)

            end_line = start_line
            for i in range(start_line + 1, n):
                stripped = lines[i].lstrip()
                if not stripped:
                    continue
                line_indent = len(lines[i].expandtabs(4)) - len(stripped)
                if line_indent <= base_indent:
                    break
                end_line = i

            frag_lines = lines[start_line: end_line + 1]
            tokens = self._tokenize_lines(frag_lines)
            frags.append(Fragment(
                file_path=file_path,
                name=name,
                start_line=start_line + 1,
                end_line=end_line + 1,
                source_lines=frag_lines,
                tokens=tokens,
            ))

        return frags

    @staticmethod
    def _tokenize_lines(lines: List[str]) -> List[str]:
        tokens = []
        for line in lines:
            line = re.sub(r'//.*$', '', line)
            line = re.sub(r'#.*$', '', line)
            tokens.extend(re.findall(r'[a-zA-Z_]\w*|[0-9]+(?:\.[0-9]+)?|[^\s\w]', line))
        return tokens