# detectors/type4/joern/extractors/feature_extractor.py

"""
Multi-Level Feature Extraction for Type-4 Clone Detection
Language-agnostic: Works for Python, Java, JavaScript, C, C++, Go, PHP

Research basis: SEED (2021), Dual-GCN (2023)
"""

from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple, Optional
import re
import logging

try:
    from ..models import PDG, MethodPDG, PDGNode, PDGEdge, EdgeType
except ImportError:
    from models import PDG, MethodPDG, PDGNode, PDGEdge, EdgeType

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """
    Extract semantic features from PDG for Type-4 detection
    
    Extracts 5 types of features:
    1. AST Features (node type distribution)
    2. Control Flow Features (CFG patterns)
    3. Data Flow Features (PDG patterns)
    4. API Call Features (library usage)
    5. Semantic Signature (high-level summary)
    """
    
    def __init__(self):
        # Language-agnostic API normalization
        self.api_normalization = self._build_api_map()
        
        # Node type categories
        self.node_categories = {
            'CONTROL': {'IF', 'ELSE', 'WHILE', 'FOR', 'DO', 'SWITCH', 'CASE'},
            'LOOP': {'WHILE', 'FOR', 'DO', 'FOREACH'},
            'CALL': {'CALL', 'METHOD_CALL'},
            'RETURN': {'RETURN'},
            'ASSIGN': {'ASSIGNMENT', 'ASSIGN', 'LOCAL'},
            'OPERATOR': {'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'MODULO'},
            'COMPARISON': {'EQUALS', 'NOT_EQUALS', 'LESS', 'GREATER'},
            'LITERAL': {'LITERAL', 'CONSTANT'}
        }
    
    def extract_all_features(self, pdg: PDG, language: str = "python") -> Dict:
        """
        Extract all feature types from PDG
        
        Args:
            pdg: Program Dependence Graph
            language: Programming language
            
        Returns:
            Dictionary with all feature types
        """
        nodes = pdg.get_all_nodes()
        edges = pdg.get_all_edges()
        
        return {
            'ast_features': self.extract_ast_features(nodes),
            'control_flow': self.extract_control_flow_features(nodes, edges),
            'data_flow': self.extract_data_flow_features(nodes, edges),
            'api_calls': self.extract_api_features(nodes, language),
            'semantic_sig': self.extract_semantic_signature(pdg, language),
            'operators': self.extract_operator_features(nodes),
            'structure': self.extract_structural_features(pdg)
        }
    
    def extract_ast_features(self, nodes: List[PDGNode]) -> Counter:
        """
        Extract AST node type distribution
        
        Returns:
            Counter of node types
        """
        features = Counter()
        
        for node in nodes:
            label = (node.label or '').upper()
            
            # Categorize node
            category = self._categorize_node(label)
            features[category] += 1
            
            # Also count specific important nodes
            if 'IF' in label:
                features['IF_COUNT'] += 1
            elif 'LOOP' in label or 'FOR' in label or 'WHILE' in label:
                features['LOOP_COUNT'] += 1
            elif 'RETURN' in label:
                features['RETURN_COUNT'] += 1
            elif 'CALL' in label:
                features['CALL_COUNT'] += 1
        
        return features
    
    def extract_control_flow_features(
        self, 
        nodes: List[PDGNode],
        edges: List[PDGEdge]
    ) -> Dict:
        """
        Extract control flow patterns
        
        Returns:
            Dictionary with control flow features
        """
        # Get control edges
        control_edges = [e for e in edges if e.edge_type == EdgeType.CONTROL]
        
        # Build node id to label map
        id_to_label = {n.id: n.label for n in nodes}
        
        # Extract control structure sequence (order matters!)
        sequence = []
        for node in sorted(nodes, key=lambda n: n.line_number or 0):
            label = (node.label or '').upper()
            if any(kw in label for kw in ['IF', 'WHILE', 'FOR', 'SWITCH', 'ELSE']):
                sequence.append(self._normalize_control_keyword(label))
        
        # Extract control flow patterns (edges between control structures)
        patterns = Counter()
        for edge in control_edges:
            src_label = id_to_label.get(edge.source_id, 'UNKNOWN')
            tgt_label = id_to_label.get(edge.target_id, 'UNKNOWN')
            
            src_cat = self._categorize_node(src_label)
            tgt_cat = self._categorize_node(tgt_label)
            
            if src_cat != 'OTHER' and tgt_cat != 'OTHER':
                patterns[(src_cat, tgt_cat)] += 1
        
        # Count nesting depth (approximation)
        nesting_depth = self._estimate_nesting_depth(nodes)
        
        return {
            'sequence': sequence,
            'patterns': patterns,
            'num_branches': sum(1 for s in sequence if s in ['IF', 'ELSE', 'SWITCH']),
            'num_loops': sum(1 for s in sequence if s in ['WHILE', 'FOR', 'DO']),
            'nesting_depth': nesting_depth,
            'num_control_edges': len(control_edges)
        }
    
    def extract_data_flow_features(
        self,
        nodes: List[PDGNode],
        edges: List[PDGEdge]
    ) -> Dict:
        """
        Extract data flow patterns
        
        Returns:
            Dictionary with data flow features
        """
        # Get data edges
        data_edges = [e for e in edges if e.edge_type == EdgeType.DATA]
        
        # Build node id to label map
        id_to_label = {n.id: n.label for n in nodes}
        
        # Extract data flow patterns (abstracted)
        patterns = set()
        for edge in data_edges:
            src_label = id_to_label.get(edge.source_id, 'VAR')
            tgt_label = id_to_label.get(edge.target_id, 'VAR')
            
            # Abstract to categories
            src_cat = self._categorize_node(src_label)
            tgt_cat = self._categorize_node(tgt_label)
            
            patterns.add((src_cat, tgt_cat))
        
        # Count variable dependencies
        var_dependencies = defaultdict(set)
        for edge in data_edges:
            if edge.variable:
                var_dependencies[edge.variable].add(edge.target_id)
        
        return {
            'patterns': patterns,
            'num_data_edges': len(data_edges),
            'num_variables': len(var_dependencies),
            'avg_dependencies': (
                sum(len(deps) for deps in var_dependencies.values()) / 
                len(var_dependencies) if var_dependencies else 0
            )
        }
    
    def extract_api_features(
        self,
        nodes: List[PDGNode],
        language: str
    ) -> Dict:
        """
        Extract API/library call features
        
        Returns:
            Dictionary with API features
        """
        api_calls = []
        
        for node in nodes:
            # Check if it's a call node
            if 'CALL' in (node.label or '').upper():
                call_name = self._extract_call_name(node.code or '')
                
                # Normalize API call (language-agnostic)
                normalized = self._normalize_api_call(call_name, language)
                api_calls.append(normalized)
        
        # Build API sequence (order matters for patterns)
        api_sequence = api_calls
        
        # Count unique APIs
        api_counts = Counter(api_calls)
        
        # Identify API patterns (common sequences)
        api_patterns = self._extract_api_patterns(api_sequence)
        
        return {
            'sequence': api_sequence,
            'counts': api_counts,
            'patterns': api_patterns,
            'num_calls': len(api_calls),
            'num_unique_apis': len(set(api_calls))
        }
    
    def extract_semantic_signature(
        self,
        pdg: PDG,
        language: str
    ) -> Set[str]:
        """
        Extract high-level semantic signature
        
        Returns:
            Set of signature tokens
        """
        signature = set()
        
        # Method signatures
        for method in pdg.methods:
            # Add method name (first 20 chars to avoid overfitting)
            method_name = method.method_name[:20] if method.method_name else ''
            if method_name and not method_name.startswith('<'):
                signature.add(f"M:{method_name}")
            
            # Add parameter count
            params = [n for n in method.nodes if 'PARAM' in (n.label or '')]
            if params:
                signature.add(f"PARAMS:{len(params)}")
            
            # Add return count
            returns = [n for n in method.nodes if 'RETURN' in (n.label or '')]
            signature.add(f"RETURNS:{len(returns)}")
        
        # Control structure counts
        nodes = pdg.get_all_nodes()
        ast_features = self.extract_ast_features(nodes)
        
        for key in ['IF_COUNT', 'LOOP_COUNT', 'CALL_COUNT']:
            if ast_features[key] > 0:
                signature.add(f"C:{key}:{ast_features[key]}")
        
        # API summary (top 5 most common)
        api_features = self.extract_api_features(nodes, language)
        top_apis = api_features['counts'].most_common(5)
        if top_apis:
            api_summary = '|'.join([api for api, _ in top_apis])
            signature.add(f"A:{api_summary}")
        
        return signature
    
    def extract_operator_features(self, nodes: List[PDGNode]) -> Counter:
        """
        Extract operator usage patterns
        
        Returns:
            Counter of operators
        """
        operators = Counter()
        
        for node in nodes:
            code = (node.code or '').lower()
            
            # Arithmetic operators
            if '+' in code:
                operators['PLUS'] += code.count('+')
            if '-' in code:
                operators['MINUS'] += code.count('-')
            if '*' in code:
                operators['MULTIPLY'] += code.count('*')
            if '/' in code:
                operators['DIVIDE'] += code.count('/')
            if '%' in code:
                operators['MODULO'] += code.count('%')
            
            # Comparison operators
            if '==' in code or '===' in code:
                operators['EQUALS'] += 1
            if '!=' in code or '!==' in code:
                operators['NOT_EQUALS'] += 1
            if '<' in code:
                operators['LESS_THAN'] += 1
            if '>' in code:
                operators['GREATER_THAN'] += 1
            
            # Logical operators
            if 'and' in code or '&&' in code:
                operators['AND'] += 1
            if 'or' in code or '||' in code:
                operators['OR'] += 1
            if 'not' in code or '!' in code:
                operators['NOT'] += 1
        
        return operators
    
    def extract_structural_features(self, pdg: PDG) -> Dict:
        """
        Extract overall structural features
        
        Returns:
            Dictionary with structural metrics
        """
        return {
            'num_methods': len(pdg.methods),
            'num_nodes': pdg.total_nodes,
            'num_edges': pdg.total_edges,
            'num_control_edges': pdg.total_control_edges,
            'num_data_edges': pdg.total_data_edges,
            'control_data_ratio': (
                pdg.total_control_edges / (pdg.total_control_edges + pdg.total_data_edges)
                if (pdg.total_control_edges + pdg.total_data_edges) > 0 else 0.5
            ),
            'avg_nodes_per_method': (
                pdg.total_nodes / len(pdg.methods) if pdg.methods else 0
            ),
            'avg_edges_per_method': (
                pdg.total_edges / len(pdg.methods) if pdg.methods else 0
            )
        }
    
    # Helper methods
    
    def _categorize_node(self, label: str) -> str:
        """Categorize node by label"""
        label = label.upper()
        
        for category, keywords in self.node_categories.items():
            if any(kw in label for kw in keywords):
                return category
        
        return 'OTHER'
    
    def _normalize_control_keyword(self, label: str) -> str:
        """Normalize control structure label"""
        label = label.upper()
        
        if 'IF' in label:
            return 'IF'
        elif 'WHILE' in label:
            return 'WHILE'
        elif 'FOR' in label:
            return 'FOR'
        elif 'SWITCH' in label:
            return 'SWITCH'
        elif 'ELSE' in label:
            return 'ELSE'
        elif 'DO' in label:
            return 'DO'
        
        return label
    
    def _estimate_nesting_depth(self, nodes: List[PDGNode]) -> int:
        """Estimate maximum nesting depth"""
        # Simple approximation using line numbers and code structure
        # In production, should use dominator tree from CFG
        max_depth = 0
        current_depth = 0
        
        for node in sorted(nodes, key=lambda n: n.line_number or 0):
            code = (node.code or '').strip()
            
            # Increase depth on control structure start
            if any(kw in code for kw in ['if ', 'while ', 'for ', 'switch ']):
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            
            # Decrease depth on closing brace (approximation)
            if code == '}' or code.endswith('}'):
                current_depth = max(0, current_depth - 1)
        
        return max_depth
    
    def _extract_call_name(self, code: str) -> str:
        """Extract function/method name from call code"""
        # Remove everything after opening parenthesis
        call_name = code.split('(')[0].strip()
        
        # Remove any leading qualifiers (e.g., object.method -> method)
        if '.' in call_name:
            call_name = call_name.split('.')[-1]
        
        # Remove any namespace qualifiers (e.g., std::cout -> cout)
        if '::' in call_name:
            call_name = call_name.split('::')[-1]
        
        return call_name.lower()
    
    def _normalize_api_call(self, call_name: str, language: str) -> str:
        """Normalize API call to language-agnostic operation"""
        # Check normalization map
        if call_name in self.api_normalization:
            return self.api_normalization[call_name]
        
        # Return original if not in map
        return call_name
    
    def _extract_api_patterns(self, api_sequence: List[str]) -> List[str]:
        """Extract common API usage patterns (3-grams)"""
        patterns = []
        
        for i in range(len(api_sequence) - 2):
            pattern = f"{api_sequence[i]}->{api_sequence[i+1]}->{api_sequence[i+2]}"
            patterns.append(pattern)
        
        return patterns
    
    def _build_api_map(self) -> Dict[str, str]:
        """
        Build language-agnostic API normalization map
        Maps language-specific APIs to generic operations
        """
        return {
            # I/O operations
            'print': 'IO_OUTPUT',
            'printf': 'IO_OUTPUT',
            'cout': 'IO_OUTPUT',
            'console.log': 'IO_OUTPUT',
            'system.out.println': 'IO_OUTPUT',
            'fmt.println': 'IO_OUTPUT',
            'echo': 'IO_OUTPUT',
            
            'input': 'IO_INPUT',
            'scanf': 'IO_INPUT',
            'cin': 'IO_INPUT',
            'console.read': 'IO_INPUT',
            'scanner.nextline': 'IO_INPUT',
            
            # Memory operations
            'malloc': 'MEM_ALLOC',
            'calloc': 'MEM_ALLOC',
            'new': 'MEM_ALLOC',
            'make': 'MEM_ALLOC',
            
            'free': 'MEM_FREE',
            'delete': 'MEM_FREE',
            
            # String operations
            'strcpy': 'STR_COPY',
            'strcat': 'STR_CONCAT',
            'strlen': 'STR_LENGTH',
            'strcmp': 'STR_COMPARE',
            'substring': 'STR_SUBSTRING',
            
            # Array/List operations
            'append': 'LIST_APPEND',
            'push': 'LIST_APPEND',
            'add': 'LIST_APPEND',
            
            'pop': 'LIST_REMOVE',
            'remove': 'LIST_REMOVE',
            
            'length': 'LIST_SIZE',
            'size': 'LIST_SIZE',
            'len': 'LIST_SIZE',
            
            # File operations
            'open': 'FILE_OPEN',
            'close': 'FILE_CLOSE',
            'read': 'FILE_READ',
            'write': 'FILE_WRITE',
            
            # Math operations
            'sqrt': 'MATH_SQRT',
            'pow': 'MATH_POW',
            'abs': 'MATH_ABS',
            'max': 'MATH_MAX',
            'min': 'MATH_MIN',
        }


def get_feature_extractor() -> FeatureExtractor:
    """Get FeatureExtractor instance"""
    return FeatureExtractor()