# detectors/type4/joern/client/joern_client.py

"""
Joern Client for PDG Extraction
FIXED VERSION - Corrects CFG extraction for recursive functions
"""

import logging
import time
from typing import Optional, Dict, Any
from pathlib import Path
import tempfile

try:
    from ..models import PDG, MethodPDG, PDGNode, PDGEdge, EdgeType, NodeType
    from ..config import get_config
    from .connection import get_container_manager
except ImportError:
    from models import PDG, MethodPDG, PDGNode, PDGEdge, EdgeType, NodeType
    from config import get_config
    from connection import get_container_manager

logger = logging.getLogger(__name__)


class JoernClient:
    """
    Client for interacting with Joern for PDG extraction
    """
    
    def __init__(self, auto_start: bool = True):
        self.config = get_config()
        self.container_manager = get_container_manager()
        self.workspace_dir = self.config.paths.workspace_dir
        self.output_dir = self.config.paths.output_dir
        
        if auto_start:
            self.ensure_container_running()
    
    def ensure_container_running(self) -> bool:
        """Ensure Joern container is running"""
        if not self.container_manager.is_container_running():
            logger.info("Starting Joern container...")
            return self.container_manager.start_container()
        return True
    
    def extract_pdg_from_code(
        self,
        code: str,
        language: str
    ) -> Optional[PDG]:
        """
        Extract PDG from code snippet
        
        Args:
            code: Source code
            language: Programming language
            
        Returns:
            PDG object or None if extraction fails
        """
        logger.info(f"Extracting PDG for {language} code")
        
        if not self.ensure_container_running():
            logger.error("Joern container not running")
            return None
        
        # Create temporary file
        ext = self._get_file_extension(language)
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix=ext,
            dir=self.workspace_dir,
            delete=False
        ) as tmp:
            tmp.write(code)
            tmp_path = Path(tmp.name)
        
        try:
            # Extract PDG
            pdg = self._extract_pdg_from_file(tmp_path, language)
            return pdg
        finally:
            # Cleanup
            if tmp_path.exists():
                tmp_path.unlink()
    
    def _extract_pdg_from_file(
        self,
        file_path: Path,
        language: str
    ) -> Optional[PDG]:
        """Extract PDG from file using Joern"""
        start_time = time.time()
        
        try:
            # Get Joern language identifier
            joern_lang = self.config.get_joern_language(language)
            
            # Build Joern query
            query = self._get_pdg_extraction_query()
            
            # Execute via container
            result = self.container_manager.exec_joern_query(
                file_path=str(file_path),
                language=joern_lang,
                query=query
            )
            
            if not result:
                logger.error("Joern query returned no result")
                return None
            
            # Parse result into PDG
            pdg = self._parse_pdg_output(result)
            pdg.file_path = str(file_path)
            pdg.language = language
            pdg.parse_time_ms = (time.time() - start_time) * 1000
            
            return pdg
            
        except Exception as e:
            logger.error(f"Error extracting PDG: {e}")
            return None
    
    def _get_pdg_extraction_query(self) -> str:
        """
        Get Joern query for PDG extraction - FIXED VERSION
        
        ✅ FIX: Properly extracts CFG edges for ALL code (including recursive)
        """
        return '''
cpg.method.l.filter { method =>
    val name = method.name
    !name.startsWith("<") && 
    !name.contains("<operator>") &&
    !name.contains("<init>") &&
    !name.contains("<module>") &&
    !name.contains("<meta>") &&
    !name.contains("<body>") &&
    name != "<global>"
}.foreach { method =>
    println(s"METHOD_START:${method.name}")
    
    // Extract AST nodes
    method.ast.l.foreach { node =>
        val line = scala.util.Try(node.lineNumber.getOrElse(-1)).getOrElse(-1)
        val code = scala.util.Try(node.code).getOrElse("").replace("\\n", " ").replace("|", "~~~").take(200)
        val label = scala.util.Try(node.label).getOrElse("UNKNOWN")
        println(s"NODE|${node.id}|${label}|${code}|${line}")
    }
    
    // ✅ FIX: Extract CFG edges properly (PRIMARY - works for all code)
    scala.util.Try {
        method.cfgNode.l.foreach { node =>
            scala.util.Try {
                node.cfgNext.l.foreach { target =>
                    println(s"CFG|${node.id}|${target.id}")
                }
            }
        }
    }
    
    // ✅ BACKUP: Also extract CDG (control dependencies) 
    scala.util.Try {
        method.ast.l.foreach { node =>
            scala.util.Try {
                node.out("CDG").l.foreach { target =>
                    println(s"CDG|${node.id}|${target.id}")
                }
            }
        }
    }
    
    // ✅ BACKUP 2: Extract dominator tree edges (for recursive)
    scala.util.Try {
        method.controlStructure.l.foreach { node =>
            scala.util.Try {
                node.astChildren.l.foreach { child =>
                    println(s"CONTROL|${node.id}|${child.id}")
                }
            }
        }
    }
    
    // Extract data flow (DDG) - UNCHANGED
    scala.util.Try {
        method.ast.l.foreach { node =>
            scala.util.Try {
                node.out("REACHING_DEF").l.foreach { target =>
                    println(s"DDG|${node.id}|${target.id}|")
                }
            }
            scala.util.Try {
                node.out("DDG").l.foreach { target =>
                    println(s"DDG|${node.id}|${target.id}|")
                }
            }
        }
    }
    
    println("METHOD_END")
}
'''
    
    def _parse_pdg_output(self, output: str) -> PDG:
        """
        Parse Joern output into PDG object - FIXED VERSION
        
        ✅ FIX: Handles CFG, CDG, and CONTROL edges
        """
        pdg = PDG()
        current_method: Optional[MethodPDG] = None
        
        for line in output.split('\n'):
            line = line.strip()
            
            if line.startswith('METHOD_START:'):
                method_name = line.split(':', 1)[1]
                current_method = MethodPDG(method_name=method_name)
                
            elif line == 'METHOD_END':
                if current_method:
                    pdg.add_method(current_method)
                current_method = None
                
            elif line.startswith('NODE|') and current_method:
                parts = line.split('|')
                if len(parts) >= 5:
                    node = PDGNode(
                        id=parts[1],
                        label=parts[2],
                        code=parts[3].replace('~~~', '|'),  # Restore pipes
                        line_number=int(parts[4]) if parts[4] != '-1' else None,
                        node_type=self._map_node_type(parts[2]),
                        method_name=current_method.method_name
                    )
                    current_method.add_node(node)
            
            # ✅ FIX: Handle CFG edges (PRIMARY SOURCE)
            elif line.startswith('CFG|') and current_method:
                parts = line.split('|')
                if len(parts) >= 3:
                    edge = PDGEdge(
                        source_id=parts[1],
                        target_id=parts[2],
                        edge_type=EdgeType.CONTROL
                    )
                    current_method.add_edge(edge)
            
            # ✅ FIX: Handle CDG edges (BACKUP)
            elif line.startswith('CDG|') and current_method:
                parts = line.split('|')
                if len(parts) >= 3:
                    edge = PDGEdge(
                        source_id=parts[1],
                        target_id=parts[2],
                        edge_type=EdgeType.CONTROL
                    )
                    current_method.add_edge(edge)
            
            # ✅ FIX: Handle CONTROL edges (BACKUP 2)
            elif line.startswith('CONTROL|') and current_method:
                parts = line.split('|')
                if len(parts) >= 3:
                    edge = PDGEdge(
                        source_id=parts[1],
                        target_id=parts[2],
                        edge_type=EdgeType.CONTROL
                    )
                    current_method.add_edge(edge)
                    
            elif line.startswith('DDG|') and current_method:
                parts = line.split('|')
                if len(parts) >= 3:
                    edge = PDGEdge(
                        source_id=parts[1],
                        target_id=parts[2],
                        edge_type=EdgeType.DATA,
                        variable=parts[3] if len(parts) > 3 else None
                    )
                    current_method.add_edge(edge)
        
        return pdg
    
    def _map_node_type(self, label: str) -> NodeType:
        """Map Joern label to NodeType"""
        label_upper = label.upper()
        
        if 'METHOD' in label_upper:
            return NodeType.METHOD
        elif 'PARAM' in label_upper:
            return NodeType.PARAMETER
        elif 'LOCAL' in label_upper or 'IDENTIFIER' in label_upper:
            return NodeType.LOCAL
        elif 'LITERAL' in label_upper:
            return NodeType.LITERAL
        elif 'CALL' in label_upper:
            return NodeType.CALL
        elif 'RETURN' in label_upper:
            return NodeType.RETURN
        elif any(kw in label_upper for kw in ['IF', 'WHILE', 'FOR', 'SWITCH']):
            return NodeType.CONTROL_STRUCTURE
        elif 'BLOCK' in label_upper:
            return NodeType.BLOCK
        elif 'ASSIGNMENT' in label_upper:
            return NodeType.ASSIGNMENT
        elif any(kw in label_upper for kw in ['PLUS', 'MINUS', 'MULT', 'DIV']):
            return NodeType.OPERATOR
        
        return NodeType.UNKNOWN
    
    def _get_file_extension(self, language: str) -> str:
        """Get file extension for language"""
        ext_map = {
            'python': '.py',
            'java': '.java',
            'javascript': '.js',
            'c': '.c',
            'cpp': '.cpp',
            'go': '.go',
            'php': '.php'
        }
        return ext_map.get(language.lower(), '.txt')
    
    def cleanup(self):
        """Cleanup temporary files"""
        # Clean workspace
        for file in self.workspace_dir.glob('*'):
            if file.is_file():
                try:
                    file.unlink()
                except:
                    pass


def get_joern_client(auto_start: bool = True) -> JoernClient:
    """Get JoernClient instance"""
    return JoernClient(auto_start)