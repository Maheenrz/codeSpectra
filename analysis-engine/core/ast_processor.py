from tree_sitter import Language, Parser
import tree_sitter_cpp
import tree_sitter_java
import tree_sitter_python
import tree_sitter_javascript
import os
import difflib

class ASTProcessor:
    def __init__(self):
        self.parsers = {}

        # Initialize Parsers
        try:
            cpp_lang = Language(tree_sitter_cpp.language())
            self.parsers['cpp'] = Parser()
            self.parsers['cpp'].set_language(cpp_lang)
        except Exception as e:
            print(f"⚠️ Warning: Could not load C++ parser: {e}")

        try:
            java_lang = Language(tree_sitter_java.language())
            self.parsers['java'] = Parser()
            self.parsers['java'].set_language(java_lang)
        except Exception as e:
            print(f"⚠️ Warning: Could not load Java parser: {e}")

        try:
            py_lang = Language(tree_sitter_python.language())
            self.parsers['python'] = Parser()
            self.parsers['python'].set_language(py_lang)
        except Exception as e:
            print(f"⚠️ Warning: Could not load Python parser: {e}")

        try:
            js_lang = Language(tree_sitter_javascript.language())
            self.parsers['javascript'] = Parser()
            self.parsers['javascript'].set_language(js_lang)
        except Exception as e:
            print(f"⚠️ Warning: Could not load JavaScript parser: {e}")

        self.ext_map = {
            '.cpp': 'cpp',
            '.c': 'cpp',
            '.h': 'cpp',
            '.hpp': 'cpp',
            '.java': 'java',
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'javascript',
        }

    def parse_file(self, file_path: str):
        abs_path = os.path.abspath(file_path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"File {file_path} not found.")

        ext = os.path.splitext(abs_path)[1].lower()
        lang_key = self.ext_map.get(ext)
        if not lang_key or lang_key not in self.parsers:
            raise ValueError(f"Unsupported language {ext} for file {file_path}. Skipping...")

        with open(file_path, "rb") as f:
            source_bytes = f.read()

        source = source_bytes.decode("utf-8", errors="ignore")

        parser = self.parsers[lang_key]
        tree = parser.parse(source_bytes)
        root = tree.root_node

        return {
            'root': root,
            'source_bytes': source_bytes,
            'source': source,
            'lang_key': lang_key,
        }

    def _node_text(self, node, source_bytes: bytes) -> str:
        return source_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="ignore")

    def _find_identifier_text(self, node, source_bytes: bytes) -> str | None:
        # DFS to find first plausible identifier token within this node
        stack = [node]
        while stack:
            n = stack.pop()
            if n.type in ('identifier', 'field_identifier', 'name', 'function_name', 'method_identifier'):
                return self._node_text(n, source_bytes).strip()
            for c in reversed(n.children):
                stack.append(c)
        return None

    def extract_functions_from_tree(self, root_node, source_bytes: bytes, lang_key: str):
        # Keep function_definition for C++ (don’t use function_declarator at top-level)
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
                results.append({
                    'name': name,
                    'start': start_line,
                    'end': end_line,
                    'node': node,
                })
                # Don’t descend into function bodies further
                continue
            # Traverse children
            stack.extend(reversed(node.children))

        return results



    def get_structure_sequence(self, file_path):
        """
        Parses the file and returns a simplified 'Skeleton String' of the logic.
        Example Output: "function_definition for_statement if_statement"
        """
        # Ensure path is absolute and exists
        abs_path = os.path.abspath(file_path)
        if not os.path.exists(abs_path):
            return ""

        ext = os.path.splitext(abs_path)[1].lower()
        lang_key = self.ext_map.get(ext)

        if not lang_key or lang_key not in self.parsers:
            return "" # Unsupported language

        try:
            with open(abs_path, 'rb') as f: # Tree-sitter expects bytes
                code = f.read()

            parser = self.parsers[lang_key]
            tree = parser.parse(code)
            
            # Walk the tree and extract ONLY structural nodes
            cursor = tree.walk()
            structure = []
            
            # Filter for relevant Control Flow nodes
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
        """
        Compares the structural skeletons of two files.
        """
        struct_a = self.get_structure_sequence(file_a)
        struct_b = self.get_structure_sequence(file_b)
        
        # If either file failed to parse or is empty, return 0 to be safe
        if not struct_a or not struct_b:
            return 0.0

        # Use SequenceMatcher to find similarity between the Skeletons
        matcher = difflib.SequenceMatcher(None, struct_a.split(), struct_b.split())
        return matcher.ratio()