"""
ASTProcessor — gracefully degrades when tree-sitter grammars are unavailable.
Uses keyword-frequency fallback on Python 3.9 in Docker.
"""
import os
import re
import difflib
from typing import Optional, Dict, Any

# Try tree-sitter (optional — only works if grammars are installed)
_TREE_SITTER_OK = False
try:
    from tree_sitter import Parser as _TSParser
    try:
        from tree_sitter_languages import get_parser as _get_parser
        _USE_GET_PARSER = True
        _TREE_SITTER_OK = True
    except ImportError:
        pass
except ImportError:
    pass

if not _TREE_SITTER_OK:
    print("⚠️  [ASTProcessor] tree-sitter not available — using keyword fallback")

_KEYWORDS: Dict[str, set] = {
    "cpp": {"for","while","do","if","else","switch","case","return","break",
            "continue","class","struct","void","int","float","double","bool",
            "true","false","nullptr","new","delete","try","catch","throw"},
    "python": {"for","while","if","elif","else","return","break","continue",
               "class","def","import","from","with","as","try","except",
               "finally","raise","yield","lambda","True","False","None"},
    "java": {"for","while","do","if","else","switch","case","return","break",
             "continue","class","interface","void","int","float","double",
             "boolean","new","try","catch","finally","throw","throws",
             "extends","implements","public","private","protected","static"},
    "javascript": {"for","while","do","if","else","switch","case","return",
                   "break","continue","class","function","const","let","var",
                   "true","false","null","undefined","new","try","catch",
                   "finally","throw","import","export","async","await"},
}

_EXT_LANG: Dict[str, str] = {
    ".cpp":"cpp",".c":"cpp",".h":"cpp",".hpp":"cpp",".cc":"cpp",".cxx":"cpp",
    ".java":"java",".py":"python",
    ".js":"javascript",".ts":"javascript",".jsx":"javascript",".tsx":"javascript",
}

def _read_source(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""

def _keyword_sequence(source: str, lang: str) -> list:
    kws = _KEYWORDS.get(lang, _KEYWORDS["cpp"])
    tokens = re.findall(r"\b\w+\b", source)
    return [t for t in tokens if t in kws]


class ASTProcessor:
    def __init__(self):
        self.parsers: Dict[str, Any] = {}
        self.ext_map = _EXT_LANG
        if _TREE_SITTER_OK:
            for lang in ["cpp", "java", "python", "javascript"]:
                try:
                    self.parsers[lang] = _get_parser(lang)
                except Exception as e:
                    print(f"⚠️  [ASTProcessor] No parser for {lang}: {e}")

    def get_structure_sequence(self, file_path: str) -> str:
        abs_path = os.path.abspath(file_path)
        if not os.path.exists(abs_path):
            return ""
        ext = os.path.splitext(abs_path)[1].lower()
        lang = self.ext_map.get(ext, "cpp")
        if lang in self.parsers:
            try:
                return self._ts_structure(abs_path, lang)
            except Exception:
                pass
        return " ".join(_keyword_sequence(_read_source(abs_path), lang))

    def calculate_similarity(self, file_a: str, file_b: str) -> float:
        seq_a = self.get_structure_sequence(file_a)
        seq_b = self.get_structure_sequence(file_b)
        if not seq_a or not seq_b:
            return 0.0
        return round(difflib.SequenceMatcher(
            None, seq_a.split(), seq_b.split(), autojunk=False
        ).ratio(), 4)

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        abs_path = os.path.abspath(file_path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        ext = os.path.splitext(abs_path)[1].lower()
        lang = self.ext_map.get(ext, "cpp")
        source = _read_source(abs_path)
        source_bytes = source.encode("utf-8", errors="ignore")
        result = {"source": source, "source_bytes": source_bytes,
                  "lang_key": lang, "root": None}
        if lang in self.parsers:
            try:
                result["root"] = self.parsers[lang].parse(source_bytes).root_node
            except Exception:
                pass
        return result

    def _ts_structure(self, abs_path: str, lang: str) -> str:
        with open(abs_path, "rb") as f:
            code = f.read()
        tree = self.parsers[lang].parse(code)
        cursor = tree.walk()
        structure = []
        relevant = {
            "function_definition","method_declaration","function_declaration",
            "method_definition","for_statement","while_statement","do_statement",
            "if_statement","else_clause","try_statement","catch_clause",
            "switch_statement","case_statement","return_statement","class_definition",
        }
        visited_children = False
        while True:
            if not visited_children:
                if cursor.node.type in relevant:
                    structure.append(cursor.node.type)
                if cursor.goto_first_child():
                    continue
            if cursor.goto_next_sibling():
                visited_children = False
            elif cursor.goto_parent():
                visited_children = True
            else:
                break
        return " ".join(structure)

    def extract_functions_from_tree(self, root_node, source_bytes: bytes, lang_key: str):
        if root_node is None:
            return []
        node_types = {
            "python": {"function_definition","class_definition"},
            "javascript": {"function_declaration","function","method_definition"},
            "java": {"method_declaration","constructor_declaration"},
            "cpp": {"function_definition","method_definition"},
        }
        types = node_types.get(lang_key, {"function_definition"})
        results, stack = [], [root_node]
        while stack:
            node = stack.pop()
            if node.type in types:
                results.append({"name": self._find_identifier_text(node, source_bytes),
                                 "start": node.start_point[0]+1,
                                 "end": node.end_point[0]+1, "node": node})
                continue
            stack.extend(reversed(node.children))
        return results

    @staticmethod
    def _node_text(node, source_bytes: bytes) -> str:
        return source_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="ignore")

    def _find_identifier_text(self, node, source_bytes: bytes) -> Optional[str]:
        stack = [node]
        while stack:
            n = stack.pop()
            if n.type in ("identifier","field_identifier","name","function_name","method_identifier"):
                return self._node_text(n, source_bytes).strip()
            for c in reversed(n.children):
                stack.append(c)
        return None