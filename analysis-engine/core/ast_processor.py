import os
import difflib
from tree_sitter_languages import get_parser

class ASTProcessor:
    def __init__(self):
        self.parsers = {
            'cpp': get_parser('cpp'),
            'java': get_parser('java'),
            'python': get_parser('python'),
            'javascript': get_parser('javascript'),
        }
        self.ext_map = {
            '.cpp': 'cpp', '.c': 'cpp', '.h': 'cpp', '.hpp': 'cpp',
            '.java': 'java', '.py': 'python',
            '.js': 'javascript', '.ts': 'javascript',
        }

    def parse_file(self, file_path: str):
        abs_path = os.path.abspath(file_path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"File {file_path} not found.")
        ext = os.path.splitext(abs_path)[1].lower()
        lang_key = self.ext_map.get(ext)
        if not lang_key or lang_key not in self.parsers:
            raise ValueError(f"Unsupported language {ext} for file {file_path}.")
        with open(abs_path, "rb") as f:
            source_bytes = f.read()
        source = source_bytes.decode("utf-8", errors="ignore")
        parser = self.parsers[lang_key]
        tree = parser.parse(source_bytes)
        root = tree.root_node
        return {'root': root, 'source_bytes': source_bytes, 'source': source, 'lang_key': lang_key}

    def _node_text(self, node, source_bytes: bytes) -> str:
        return source_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="ignore")

    def _find_identifier_text(self, node, source_bytes: bytes) -> str | None:
        stack = [node]
        while stack:
            n = stack.pop()
            if n.type in ('identifier', 'field_identifier', 'name', 'function_name', 'method_identifier'):
                return self._node_text(n, source_bytes).strip()
            for c in reversed(n.children):
                stack.append(c)
        return None

    def extract_functions_from_tree(self, root_node, source_bytes: bytes, lang_key: str):
        node_types = {
            'python': {'function_definition', 'class_definition'},
            'javascript': {'function_declaration', 'function', 'method_definition'},
            'java': {'method_declaration', 'constructor_declaration'},
            'cpp': {'function_definition', 'method_definition'},
        }
        types = node_types.get(lang_key, {'function_definition'})
        results = []
        stack = [root_node]
        while stack:
            node = stack.pop()
            if node.type in types:
                start_line = node.start_point[0] + 1
                end_line = node.end_point[0] + 1
                name = self._find_identifier_text(node, source_bytes)
                results.append({'name': name, 'start': start_line, 'end': end_line, 'node': node})
                continue
            stack.extend(reversed(node.children))
        return results

    def get_structure_sequence(self, file_path):
        abs_path = os.path.abspath(file_path)
        if not os.path.exists(abs_path):
            return ""
        ext = os.path.splitext(abs_path)[1].lower()
        lang_key = self.ext_map.get(ext)
        if not lang_key or lang_key not in self.parsers:
            return ""
        try:
            with open(abs_path, 'rb') as f:
                code = f.read()
            parser = self.parsers[lang_key]
            tree = parser.parse(code)
            cursor = tree.walk()
            structure = []
            relevant_types = {
                'function_definition', 'method_declaration',
                'for_statement', 'while_statement', 'do_statement',
                'if_statement', 'else_clause',
                'try_statement', 'catch_clause',
                'switch_statement', 'case_statement',
                'return_statement', 'class_definition'
            }
            visited_children = False
            while True:
                if not visited_children:
                    if cursor.node.type in relevant_types:
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
        except Exception as e:
            print(f"Error parsing AST for {file_path}: {e}")
            return ""

    def calculate_similarity(self, file_a, file_b):
        struct_a = self.get_structure_sequence(file_a)
        struct_b = self.get_structure_sequence(file_b)
        if not struct_a or not struct_b:
            return 0.0
        matcher = difflib.SequenceMatcher(None, struct_a.split(), struct_b.split())
        return matcher.ratio()