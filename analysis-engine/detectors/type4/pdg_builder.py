# analysis-engine/detectors/type4/pdg_builder.py

"""
Simplified PDG (Program Dependence Graph) Builder

Converts source code into a graph representation that captures:
1. Control Dependencies: Which statements control which others
2. Data Dependencies: Which statements share data through variables

This is a LIGHTWEIGHT implementation that doesn't require heavy frameworks
like LLVM or Soot. It uses regex-based parsing to extract semantic information.
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Any, Tuple
from pathlib import Path


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class PDGNode:
    """
    Represents a node (statement) in the Program Dependence Graph.
    
    Each significant line of code becomes a node with:
    - Type: What kind of statement (loop, condition, assignment, etc.)
    - Variables: What variables it defines and uses
    - Calls: What functions it calls
    """
    id: int
    node_type: str              # 'loop', 'condition', 'assignment', 'return', 'call', 'statement'
    line_number: int
    code_snippet: str           # First 100 chars of the line
    variables_defined: Set[str] = field(default_factory=set)
    variables_used: Set[str] = field(default_factory=set)
    function_calls: List[str] = field(default_factory=list)


@dataclass
class PDGEdge:
    """
    Represents a dependency edge in the PDG.
    
    Two types:
    - Data Edge: Node A defines variable X, Node B uses variable X
    - Control Edge: Node A (if/loop) controls execution of Node B
    """
    from_node: int
    to_node: int
    edge_type: str              # 'data' or 'control'
    variable: Optional[str] = None  # For data edges, which variable


@dataclass
class SimplifiedPDG:
    """
    The complete Simplified Program Dependence Graph.
    
    Contains:
    - nodes: All significant statements
    - edges: All dependencies between statements
    - Metadata: Control signature, counts, etc.
    """
    file_path: str
    language: str
    nodes: List[PDGNode] = field(default_factory=list)
    edges: List[PDGEdge] = field(default_factory=list)
    
    # Control flow metadata
    control_flow_signature: str = ""
    loop_count: int = 0
    condition_count: int = 0
    max_nesting_depth: int = 0
    
    # Data flow metadata
    total_variables: int = 0
    total_data_dependencies: int = 0
    
    # Call metadata
    function_calls: List[str] = field(default_factory=list)
    recursion_detected: bool = False
    
    # Structural metadata
    return_count: int = 0


# =============================================================================
# LANGUAGE PATTERNS
# =============================================================================

class LanguagePatterns:
    """
    Regex patterns for different programming languages.
    Used to identify code constructs without full parsing.
    """
    
    PATTERNS = {
        'cpp': {
            'loop_for': r'\bfor\s*\(',
            'loop_while': r'\bwhile\s*\(',
            'loop_do': r'\bdo\s*\{',
            'condition_if': r'\bif\s*\(',
            'condition_elif': r'\belse\s+if\s*\(',
            'condition_else': r'\belse\s*\{',
            'condition_switch': r'\bswitch\s*\(',
            'function_def': r'(?:[\w\s\*&:<>]+)\s+(\w+)\s*\([^;{]*\)\s*(?:const)?\s*(?:override)?\s*\{',
            'function_call': r'\b(\w+)\s*\([^;]*\)',
            'return_stmt': r'\breturn\b',
            'assignment': r'(\b[a-zA-Z_]\w*)\s*(?:\+|-|\*|/|%|&|\||\^)?=(?!=)',
            'variable_decl': r'(?:int|float|double|char|bool|long|short|unsigned|auto|string|vector|map|set)\s+(\w+)',
            'identifier': r'\b([a-zA-Z_]\w*)\b',
        },
        'java': {
            'loop_for': r'\bfor\s*\(',
            'loop_while': r'\bwhile\s*\(',
            'loop_do': r'\bdo\s*\{',
            'condition_if': r'\bif\s*\(',
            'condition_elif': r'\belse\s+if\s*\(',
            'condition_else': r'\belse\s*\{',
            'condition_switch': r'\bswitch\s*\(',
            'function_def': r'(?:public|private|protected)?\s*(?:static)?\s*(?:final)?\s*\w+(?:<[^>]+>)?\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+\w+)?\s*\{',
            'function_call': r'\b(\w+)\s*\([^;]*\)',
            'return_stmt': r'\breturn\b',
            'assignment': r'(\b[a-zA-Z_]\w*)\s*(?:\+|-|\*|/|%|&|\||\^)?=(?!=)',
            'variable_decl': r'(?:int|float|double|char|boolean|long|short|byte|String|List|Map|Set|Array)\s+(\w+)',
            'identifier': r'\b([a-zA-Z_]\w*)\b',
        },
        'python': {
            'loop_for': r'\bfor\s+\w+\s+in\b',
            'loop_while': r'\bwhile\s+',
            'loop_do': None,  # Python doesn't have do-while
            'condition_if': r'\bif\s+',
            'condition_elif': r'\belif\s+',
            'condition_else': r'\belse\s*:',
            'condition_switch': None,  # Python doesn't have switch (until 3.10 match)
            'function_def': r'def\s+(\w+)\s*\(',
            'function_call': r'\b(\w+)\s*\([^)]*\)',
            'return_stmt': r'\breturn\b',
            'assignment': r'(\b[a-zA-Z_]\w*)\s*(?:\+|-|\*|/|%|&|\||\^)?=(?!=)',
            'variable_decl': None,  # Python doesn't have type declarations (mostly)
            'identifier': r'\b([a-zA-Z_]\w*)\b',
        },
        'c': {
            'loop_for': r'\bfor\s*\(',
            'loop_while': r'\bwhile\s*\(',
            'loop_do': r'\bdo\s*\{',
            'condition_if': r'\bif\s*\(',
            'condition_elif': r'\belse\s+if\s*\(',
            'condition_else': r'\belse\s*\{',
            'condition_switch': r'\bswitch\s*\(',
            'function_def': r'(?:[\w\s\*]+)\s+(\w+)\s*\([^;{]*\)\s*\{',
            'function_call': r'\b(\w+)\s*\([^;]*\)',
            'return_stmt': r'\breturn\b',
            'assignment': r'(\b[a-zA-Z_]\w*)\s*(?:\+|-|\*|/|%|&|\||\^)?=(?!=)',
            'variable_decl': r'(?:int|float|double|char|long|short|unsigned|signed)\s+(\w+)',
            'identifier': r'\b([a-zA-Z_]\w*)\b',
        },
    }
    
    # Keywords to exclude from variable detection (per language)
    KEYWORDS = {
        'cpp': {
            'int', 'float', 'double', 'char', 'void', 'bool', 'long', 'short',
            'unsigned', 'signed', 'const', 'static', 'extern', 'register',
            'volatile', 'inline', 'virtual', 'override', 'final', 'explicit',
            'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'default',
            'break', 'continue', 'return', 'goto', 'throw', 'try', 'catch',
            'class', 'struct', 'union', 'enum', 'namespace', 'using', 'typedef',
            'public', 'private', 'protected', 'friend', 'template', 'typename',
            'new', 'delete', 'this', 'nullptr', 'true', 'false', 'sizeof',
            'auto', 'decltype', 'constexpr', 'noexcept', 'operator',
            'vector', 'string', 'map', 'set', 'pair', 'array', 'list', 'deque',
            'queue', 'stack', 'priority_queue', 'unordered_map', 'unordered_set',
            'cout', 'cin', 'endl', 'std', 'printf', 'scanf', 'main',
            'include', 'define', 'ifdef', 'ifndef', 'endif', 'pragma',
            'max', 'min', 'abs', 'sort', 'find', 'begin', 'end', 'size', 'push_back',
            'INT_MIN', 'INT_MAX', 'LLONG_MIN', 'LLONG_MAX', 'NULL',
        },
        'java': {
            'int', 'float', 'double', 'char', 'void', 'boolean', 'long', 'short', 'byte',
            'final', 'static', 'abstract', 'synchronized', 'volatile', 'transient',
            'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'default',
            'break', 'continue', 'return', 'throw', 'try', 'catch', 'finally',
            'class', 'interface', 'enum', 'extends', 'implements', 'package', 'import',
            'public', 'private', 'protected', 'new', 'this', 'super',
            'null', 'true', 'false', 'instanceof', 'assert', 'native', 'strictfp',
            'String', 'Integer', 'Long', 'Double', 'Float', 'Boolean', 'Character',
            'List', 'ArrayList', 'LinkedList', 'Map', 'HashMap', 'TreeMap',
            'Set', 'HashSet', 'TreeSet', 'Array', 'Arrays', 'Collections',
            'System', 'out', 'println', 'print', 'Math', 'main', 'args',
            'Override', 'Deprecated', 'SuppressWarnings',
        },
        'python': {
            'def', 'class', 'if', 'elif', 'else', 'for', 'while', 'try', 'except',
            'finally', 'with', 'as', 'import', 'from', 'return', 'yield', 'raise',
            'pass', 'break', 'continue', 'and', 'or', 'not', 'in', 'is', 'lambda',
            'global', 'nonlocal', 'assert', 'async', 'await', 'del',
            'True', 'False', 'None',
            'self', 'cls', '__init__', '__main__', '__name__',
            'print', 'input', 'len', 'range', 'enumerate', 'zip', 'map', 'filter',
            'str', 'int', 'float', 'bool', 'list', 'dict', 'set', 'tuple', 'type',
            'open', 'file', 'read', 'write', 'close',
            'sorted', 'reversed', 'sum', 'max', 'min', 'abs', 'round',
            'append', 'extend', 'insert', 'remove', 'pop', 'clear',
            'keys', 'values', 'items', 'get', 'update',
        },
        'c': {
            'int', 'float', 'double', 'char', 'void', 'long', 'short',
            'unsigned', 'signed', 'const', 'static', 'extern', 'register',
            'volatile', 'auto', 'typedef', 'sizeof',
            'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'default',
            'break', 'continue', 'return', 'goto',
            'struct', 'union', 'enum',
            'NULL', 'true', 'false',
            'printf', 'scanf', 'fprintf', 'fscanf', 'sprintf', 'sscanf',
            'malloc', 'calloc', 'realloc', 'free',
            'strlen', 'strcpy', 'strcat', 'strcmp', 'memcpy', 'memset',
            'fopen', 'fclose', 'fread', 'fwrite', 'fgets', 'fputs',
            'main', 'include', 'define', 'ifdef', 'ifndef', 'endif', 'pragma',
            'INT_MIN', 'INT_MAX', 'LONG_MIN', 'LONG_MAX',
        },
    }
    
    @classmethod
    def get_patterns(cls, language: str) -> Dict[str, Optional[str]]:
        """Get patterns for a specific language"""
        return cls.PATTERNS.get(language, cls.PATTERNS['cpp'])
    
    @classmethod
    def get_keywords(cls, language: str) -> Set[str]:
        """Get keywords for a specific language"""
        return cls.KEYWORDS.get(language, cls.KEYWORDS['cpp'])


# =============================================================================
# PDG BUILDER
# =============================================================================

class PDGBuilder:
    """
    Builds a Simplified PDG from source code.
    
    The builder:
    1. Reads code line by line
    2. Identifies significant statements (loops, conditions, assignments, etc.)
    3. Creates nodes for each statement
    4. Tracks variable definitions and uses
    5. Creates edges for data and control dependencies
    """

    BOILERPLATE_CALLS = {
        'cpp': {
            'cin', 'cout', 'printf', 'scanf', 'getline', 'puts', 'gets',
            'endl', 'flush', 'begin', 'end', 'size', 'length', 'empty', 
            'clear', 'push_back', 'pop_back', 'front', 'back', 'insert', 
            'erase', 'find', 'count', 'new', 'delete', 'malloc', 'free',
        },
        'java': {
            'println', 'print', 'printf', 'nextInt', 'nextLine', 'next',
            'hasNext', 'close', 'toString', 'equals', 'hashCode',
            'size', 'length', 'isEmpty', 'clear', 'add', 'remove', 'get',
        },
        'python': {
            'print', 'input', 'open', 'read', 'write', 'close',
            'len', 'range', 'enumerate', 'zip', 'str', 'int', 'float',
            'list', 'dict', 'set', 'append', 'extend', 'pop', 'remove',
        },
        'c': {
            'printf', 'scanf', 'fprintf', 'fscanf', 'fgets', 'fputs',
            'fopen', 'fclose', 'malloc', 'calloc', 'free', 'memset',
        }
    }
    
    def __init__(self):
        self.patterns = LanguagePatterns()
    
    def detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        ext = Path(file_path).suffix.lower()
        ext_map = {
            '.cpp': 'cpp', '.cc': 'cpp', '.cxx': 'cpp', 
            '.hpp': 'cpp', '.h': 'cpp', '.hxx': 'cpp',
            '.java': 'java',
            '.py': 'python',
            '.c': 'c',
        }
        return ext_map.get(ext, 'cpp')
    
    def build_from_file(self, file_path: str) -> SimplifiedPDG:
        """
        Build PDG from a source code file.
        
        Args:
            file_path: Path to the source file
            
        Returns:
            SimplifiedPDG object
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
            
            language = self.detect_language(file_path)
            pdg = self.build_from_code(code, language, file_path)
            return pdg
            
        except Exception as e:
            print(f"⚠️ Error building PDG from {file_path}: {e}")
            return SimplifiedPDG(file_path=file_path, language='unknown')
    
    def build_from_code(
        self, 
        code: str, 
        language: str, 
        file_path: str = "unknown"
    ) -> SimplifiedPDG:
        """
        Build PDG from source code string.
        
        This is the main building method that:
        1. Parses code line by line
        2. Creates nodes for significant statements
        3. Tracks variable definitions and uses
        4. Builds dependency edges
        """
        
        patterns = self.patterns.get_patterns(language)
        keywords = self.patterns.get_keywords(language)
        
        lines = code.splitlines()
        nodes: List[PDGNode] = []
        
        # Tracking state
        node_id = 0
        variable_definitions: Dict[str, int] = {}  # var_name -> most recent node_id
        control_stack: List[Tuple[int, str]] = []  # (node_id, type) for nesting
        current_nesting = 0
        max_nesting = 0
        all_function_calls: List[str] = []
        
        # Detect function names for recursion detection
        func_def_pattern = patterns.get('function_def')
        defined_functions: Set[str] = set()
        if func_def_pattern:
            for match in re.finditer(func_def_pattern, code):
                defined_functions.add(match.group(1))
        
        # Track brace depth for nesting (for C-like languages)
        brace_depth = 0
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Skip empty lines and comments
            if not stripped:
                continue
            if self._is_comment(stripped, language):
                continue
            
            # Track braces for nesting depth
            brace_depth += stripped.count('{') - stripped.count('}')
            
            # Determine node type
            node_type = self._determine_node_type(stripped, patterns, language)
            
            # Update nesting tracking
            if node_type in ['loop', 'condition']:
                current_nesting += 1
                max_nesting = max(max_nesting, current_nesting)
                control_stack.append((node_id, node_type))
            
            # Check for block end (simplified)
            if stripped == '}' or (language == 'python' and stripped.startswith('return')):
                if current_nesting > 0 and node_type not in ['loop', 'condition']:
                    current_nesting = max(0, current_nesting - 1)
            
            # Extract variables defined in this line
            vars_defined = self._extract_defined_variables(stripped, patterns, keywords)
            
            # Extract variables used in this line
            vars_used = self._extract_used_variables(stripped, patterns, keywords, vars_defined)
            
            # Extract function calls
            calls = self._extract_function_calls(stripped, patterns, keywords)
            all_function_calls.extend(calls)
            
            # Only create nodes for significant statements
            if node_type != 'skip' and (node_type != 'statement' or vars_defined or calls):
                node = PDGNode(
                    id=node_id,
                    node_type=node_type,
                    line_number=line_num,
                    code_snippet=stripped[:100],
                    variables_defined=vars_defined,
                    variables_used=vars_used,
                    function_calls=calls
                )
                nodes.append(node)
                
                # Update variable definitions tracking
                for var in vars_defined:
                    variable_definitions[var] = node_id
                
                node_id += 1
        
        # Build edges
        edges = self._build_edges(nodes, variable_definitions)
        
        # Build control flow signature
        control_signature = self._build_control_signature(nodes)
        
        # Check for recursion
        recursion_detected = bool(defined_functions & set(all_function_calls))
        
        # Count statistics
        loop_count = sum(1 for n in nodes if n.node_type == 'loop')
        condition_count = sum(1 for n in nodes if n.node_type == 'condition')
        return_count = sum(1 for n in nodes if n.node_type == 'return')
        data_edges = sum(1 for e in edges if e.edge_type == 'data')
        
        # Collect all unique variables
        all_variables: Set[str] = set()
        for node in nodes:
            all_variables.update(node.variables_defined)
            all_variables.update(node.variables_used)
        
        return SimplifiedPDG(
            file_path=file_path,
            language=language,
            nodes=nodes,
            edges=edges,
            control_flow_signature=control_signature,
            loop_count=loop_count,
            condition_count=condition_count,
            max_nesting_depth=max_nesting,
            total_variables=len(all_variables),
            total_data_dependencies=data_edges,
            function_calls=list(set(all_function_calls)),
            recursion_detected=recursion_detected,
            return_count=return_count
        )
    
    def _is_comment(self, line: str, language: str) -> bool:
        """Check if a line is a comment"""
        if language == 'python':
            return line.startswith('#')
        else:
            return (
                line.startswith('//') or 
                line.startswith('/*') or 
                line.startswith('*') or
                line.startswith('#include') or
                line.startswith('#define') or
                line.startswith('#pragma')
            )
    
    def _determine_node_type(
        self, 
        line: str, 
        patterns: Dict[str, Optional[str]],
        language: str
    ) -> str:
        """
        Determine the type of statement from a line of code.
        
        Returns: 'loop', 'condition', 'assignment', 'return', 'call', 'statement', or 'skip'
        """
        
        # Skip certain lines
        if line in ['{', '}', '};', '']:
            return 'skip'
        if line.startswith('//') or line.startswith('#'):
            return 'skip'
        
        # Check for loops
        for pattern_key in ['loop_for', 'loop_while', 'loop_do']:
            pattern = patterns.get(pattern_key)
            if pattern and re.search(pattern, line):
                return 'loop'
        
        # Check for conditions
        for pattern_key in ['condition_if', 'condition_elif', 'condition_switch']:
            pattern = patterns.get(pattern_key)
            if pattern and re.search(pattern, line):
                return 'condition'
        
        # Check for return
        pattern = patterns.get('return_stmt')
        if pattern and re.search(pattern, line):
            return 'return'
        
        # Check for assignment
        pattern = patterns.get('assignment')
        if pattern and re.search(pattern, line):
            return 'assignment'
        
        # Check for function call (that's not part of something else)
        pattern = patterns.get('function_call')
        if pattern and re.search(pattern, line):
            return 'call'
        
        return 'statement'
    
    def _extract_defined_variables(
        self,
        line: str,
        patterns: Dict[str, Optional[str]],
        keywords: Set[str]
    ) -> Set[str]:
        """Extract variables that are defined/assigned in this line"""
        defined = set()
        
        # Check for explicit variable declarations
        decl_pattern = patterns.get('variable_decl')
        if decl_pattern:
            for match in re.finditer(decl_pattern, line):
                var = match.group(1)
                if var not in keywords:
                    defined.add(var)
        
        # Check for assignments
        assign_pattern = patterns.get('assignment')
        if assign_pattern:
            for match in re.finditer(assign_pattern, line):
                var = match.group(1)
                if var not in keywords and not var.isupper():  # Skip constants
                    defined.add(var)
        
        return defined
    
    def _extract_used_variables(
        self,
        line: str,
        patterns: Dict[str, Optional[str]],
        keywords: Set[str],
        defined_in_line: Set[str]
    ) -> Set[str]:
        """Extract variables that are used (read) in this line"""
        used = set()
        
        # Find all identifiers
        id_pattern = patterns.get('identifier')
        if id_pattern:
            for match in re.finditer(id_pattern, line):
                var = match.group(1)
                # Exclude keywords, defined vars, constants, and function calls
                if (var not in keywords and 
                    var not in defined_in_line and 
                    not var.isupper() and  # Skip constants like INT_MAX
                    not var[0].isupper() and  # Skip class names
                    len(var) > 1):  # Skip single char that might be type
                    used.add(var)
        
        return used
    
    def _extract_function_calls(
        self,
        line: str,
        patterns: Dict[str, Optional[str]],
        keywords: Set[str],
        language: str = 'cpp'  # ADD this parameter
    ) -> List[str]:
        """Extract function calls from a line (with boilerplate filtering)"""
        calls = []
        
        # Get boilerplate calls for this language
        boilerplate = self.BOILERPLATE_CALLS.get(language, set())
        
        pattern = patterns.get('function_call')
        if pattern:
            for match in re.finditer(pattern, line):
                func = match.group(1)
                # Exclude keywords, boilerplate, and common non-functions
                if (func not in keywords and 
                    func not in boilerplate and  # NEW: Filter boilerplate
                    not func.isupper() and
                    func not in ['if', 'for', 'while', 'switch', 'catch']):
                    calls.append(func)
        
        return calls
    
    def _build_edges(
        self,
        nodes: List[PDGNode],
        variable_definitions: Dict[str, int]
    ) -> List[PDGEdge]:
        """
        Build dependency edges between nodes.
        
        Creates:
        1. Data edges: When a variable defined in node A is used in node B
        2. Control edges: When a loop/condition controls subsequent statements
        """
        edges = []
        
        # Track latest definition of each variable
        var_latest_def: Dict[str, int] = {}
        
        for node in nodes:
            # Update definitions first
            for var in node.variables_defined:
                var_latest_def[var] = node.id
            
            # Create data dependency edges for used variables
            for var in node.variables_used:
                if var in var_latest_def and var_latest_def[var] != node.id:
                    edges.append(PDGEdge(
                        from_node=var_latest_def[var],
                        to_node=node.id,
                        edge_type='data',
                        variable=var
                    ))
        
        # Create control dependency edges (simplified)
        control_stack: List[int] = []
        
        for i, node in enumerate(nodes):
            # If this is a control node, it controls the next few nodes
            if node.node_type in ['loop', 'condition']:
                control_stack.append(node.id)
                
                # Control the next 5-10 nodes (simplified)
                for j in range(i + 1, min(i + 8, len(nodes))):
                    edges.append(PDGEdge(
                        from_node=node.id,
                        to_node=nodes[j].id,
                        edge_type='control'
                    ))
        
        return edges
    
    def _build_control_signature(self, nodes: List[PDGNode]) -> str:
        """
        Build a signature string representing the control flow structure.
        
        Each character represents a control structure:
        - L: Loop
        - C: Condition  
        - R: Return
        """
        signature_chars = []
        
        for node in nodes:
            if node.node_type == 'loop':
                signature_chars.append('L')
            elif node.node_type == 'condition':
                signature_chars.append('C')
            elif node.node_type == 'return':
                signature_chars.append('R')
        
        return ''.join(signature_chars)