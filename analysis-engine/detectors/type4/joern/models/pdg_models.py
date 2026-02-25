# detectors/type4/joern/models/pdg_models.py

"""
Data models for Program Dependence Graph (PDG)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Any
from enum import Enum


class EdgeType(Enum):
    """Types of edges in PDG"""
    CONTROL = "control"
    DATA = "data"
    CALL = "call"
    RETURN = "return"


class NodeType(Enum):
    """Types of nodes in PDG"""
    METHOD = "METHOD"
    PARAMETER = "PARAMETER"
    LOCAL = "LOCAL"
    LITERAL = "LITERAL"
    IDENTIFIER = "IDENTIFIER"
    CALL = "CALL"
    RETURN = "RETURN"
    CONTROL_STRUCTURE = "CONTROL_STRUCTURE"
    BLOCK = "BLOCK"
    ASSIGNMENT = "ASSIGNMENT"
    OPERATOR = "OPERATOR"
    UNKNOWN = "UNKNOWN"


@dataclass
class PDGNode:
    """
    Represents a node in the Program Dependence Graph
    """
    id: str
    code: str
    label: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    node_type: NodeType = NodeType.UNKNOWN
    method_name: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if isinstance(other, PDGNode):
            return self.id == other.id
        return False
    
    def get_normalized_code(self) -> str:
        """Get normalized code for comparison"""
        return ' '.join(self.code.lower().split())


@dataclass
class PDGEdge:
    """
    Represents an edge in the Program Dependence Graph
    """
    source_id: str
    target_id: str
    edge_type: EdgeType
    variable: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def __hash__(self):
        return hash((self.source_id, self.target_id, self.edge_type))
    
    def __eq__(self, other):
        if isinstance(other, PDGEdge):
            return (
                self.source_id == other.source_id and
                self.target_id == other.target_id and
                self.edge_type == other.edge_type
            )
        return False


@dataclass
class ControlEdge(PDGEdge):
    """Control dependency edge"""
    
    def __init__(self, source_id: str, target_id: str, **kwargs):
        super().__init__(
            source_id=source_id,
            target_id=target_id,
            edge_type=EdgeType.CONTROL,
            **kwargs
        )


@dataclass
class DataEdge(PDGEdge):
    """Data dependency edge"""
    
    def __init__(self, source_id: str, target_id: str, variable: str = None, **kwargs):
        super().__init__(
            source_id=source_id,
            target_id=target_id,
            edge_type=EdgeType.DATA,
            variable=variable,
            **kwargs
        )


@dataclass
class MethodPDG:
    """
    PDG for a single method/function
    """
    method_name: str
    file_name: Optional[str] = None
    nodes: List[PDGNode] = field(default_factory=list)
    edges: List[PDGEdge] = field(default_factory=list)
    control_edges: List[PDGEdge] = field(default_factory=list)
    data_edges: List[PDGEdge] = field(default_factory=list)
    
    def __post_init__(self):
        self._categorize_edges()
    
    def _categorize_edges(self):
        self.control_edges = [e for e in self.edges if e.edge_type == EdgeType.CONTROL]
        self.data_edges = [e for e in self.edges if e.edge_type == EdgeType.DATA]
    
    def add_node(self, node: PDGNode):
        self.nodes.append(node)
    
    def add_edge(self, edge: PDGEdge):
        self.edges.append(edge)
        if edge.edge_type == EdgeType.CONTROL:
            self.control_edges.append(edge)
        elif edge.edge_type == EdgeType.DATA:
            self.data_edges.append(edge)
    
    def get_node_by_id(self, node_id: str) -> Optional[PDGNode]:
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
    
    def get_node_codes(self) -> Set[str]:
        return {node.get_normalized_code() for node in self.nodes}
    
    @property
    def num_nodes(self) -> int:
        return len(self.nodes)
    
    @property
    def num_edges(self) -> int:
        return len(self.edges)
    
    @property
    def num_control_edges(self) -> int:
        return len(self.control_edges)
    
    @property
    def num_data_edges(self) -> int:
        return len(self.data_edges)


@dataclass
class PDG:
    """
    Complete Program Dependence Graph for a code file
    """
    file_path: Optional[str] = None
    language: Optional[str] = None
    methods: List[MethodPDG] = field(default_factory=list)
    parse_time_ms: Optional[float] = None
    joern_version: Optional[str] = None
    
    def add_method(self, method_pdg: MethodPDG):
        self.methods.append(method_pdg)
    
    def get_method(self, method_name: str) -> Optional[MethodPDG]:
        for method in self.methods:
            if method.method_name == method_name:
                return method
        return None
    
    def get_all_nodes(self) -> List[PDGNode]:
        nodes = []
        for method in self.methods:
            nodes.extend(method.nodes)
        return nodes
    
    def get_all_edges(self) -> List[PDGEdge]:
        edges = []
        for method in self.methods:
            edges.extend(method.edges)
        return edges
    
    @property
    def total_nodes(self) -> int:
        return sum(m.num_nodes for m in self.methods)
    
    @property
    def total_edges(self) -> int:
        return sum(m.num_edges for m in self.methods)
    
    @property
    def total_control_edges(self) -> int:
        return sum(m.num_control_edges for m in self.methods)
    
    @property
    def total_data_edges(self) -> int:
        return sum(m.num_data_edges for m in self.methods)
    
    def get_statistics(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "language": self.language,
            "num_methods": len(self.methods),
            "total_nodes": self.total_nodes,
            "total_edges": self.total_edges,
            "control_edges": self.total_control_edges,
            "data_edges": self.total_data_edges,
            "parse_time_ms": self.parse_time_ms
        }