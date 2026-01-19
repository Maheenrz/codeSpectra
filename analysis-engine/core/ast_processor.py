# ast-processor.py
from tree_sitter import Language, Parser
import tree_sitter_cpp
import tree_sitter_java
import tree_sitter_python
import tree_sitter_javascript
import difflib
import os

class ASTProcessor:
    def __init__(self):
        # Initialize Parsers for supported languages
        self.parsers = {}
        
        # ---------------------------------------------------------
        # FIX: Wrap the raw 'language()' output in Language() class
        # ---------------------------------------------------------

        # C++
        try:
            cpp_lang = Language(tree_sitter_cpp.language())
            self.parsers['cpp'] = Parser(cpp_lang)
        except Exception as e:
            print(f"⚠️ Warning: Could not load C++ parser: {e}")
        
        # Java
        try:
            java_lang = Language(tree_sitter_java.language())
            self.parsers['java'] = Parser(java_lang)
        except Exception as e:
            print(f"⚠️ Warning: Could not load Java parser: {e}")
        
        # Python
        try:
            py_lang = Language(tree_sitter_python.language())
            self.parsers['python'] = Parser(py_lang)
        except Exception as e:
            print(f"⚠️ Warning: Could not load Python parser: {e}")

        # JS/TS
        try:
            js_lang = Language(tree_sitter_javascript.language())
            self.parsers['javascript'] = Parser(js_lang)
        except Exception as e:
            print(f"⚠️ Warning: Could not load JS parser: {e}")

        # Map typical file extensions to our internal keys
        self.ext_map = {
            '.cpp': 'cpp', '.c': 'cpp', '.h': 'cpp', '.hpp': 'cpp',
            '.java': 'java',
            '.py': 'python',
            '.js': 'javascript', '.ts': 'javascript'
        }

    def parse_file(self, file_path: str):
        """
        Parse file and return a dict with:
        - 'root': root_node (tree-sitter)
        - 'source_bytes': raw bytes
        - 'source': decoded text (utf-8, ignore errors)
        - 'lang_key': detected language key ('cpp','python','java','javascript')
        """
        abs_path = os.path.abspath(file_path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(abs_path)

        ext = os.path.splitext(abs_path)[1].lower()
        lang_key = self.ext_map.get(ext)
        if not lang_key or lang_key not in self.parsers:
            raise ValueError(f"Unsupported language or parser not loaded for extension {ext}")

        with open(abs_path, "rb") as f:
            source_bytes = f.read()
        source = source_bytes.decode("utf-8", errors="ignore")

        parser = self.parsers[lang_key]  # this is a tree-sitter Parser instance you created
        tree = parser.parse(source_bytes)
        root = tree.root_node
        return {'root': root, 'source_bytes': source_bytes, 'source': source, 'lang_key': lang_key}


    def extract_functions_from_tree(self, root_node, source_bytes: bytes, lang_key: str):
        """
        Walk the tree-sitter root_node and return a list of function dicts:
        [{'name': <str or None>, 'start': <int line>, 'end': <int line>, 'node': node}, ...]
        Lines are 1-based.
        This uses a small set of node.type names per language (may need tuning).
        """
        # per-language function node types (add more if needed)
        func_node_types = {
            'python': {'function_definition', 'class_definition'},
            'javascript': {'function_declaration', 'function', 'method_definition'},
            'java': {'method_declaration', 'constructor_declaration'},
            'cpp': {'function_definition', 'function_declarator', 'function_definition', 'method_definition'}
        }
        types = func_node_types.get(lang_key, {'function_definition'})

        results = []
        # simple iterative traversal
        stack = [root_node]
        while stack:
            node = stack.pop()
            if node.type in types:
                # start_point and end_point are (row, column), row is 0-based
                start_line = node.start_point[0] + 1
                end_line = node.end_point[0] + 1
                # try to get a name if available (search child identifier)
                name = None
                for child in node.children:
                    if child.type in ('identifier', 'name', 'function_name', 'method_identifier'):
                        try:
                            name = source_bytes[child.start_byte:child.end_byte].decode('utf-8', errors='ignore')
                        except Exception:
                            name = None
                        break
                results.append({'name': name, 'start': start_line, 'end': end_line, 'node': node})
                # do not descend into this function node by default
                continue
            # push children
            for c in reversed(node.children):
                stack.append(c)
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