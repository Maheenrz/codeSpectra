# detectors/type4/joern/client/joern_client.py

"""
Joern client for code analysis and PDG extraction
"""

import os
import json
import tempfile
import logging
import re
from typing import Dict, List, Optional, Any
from pathlib import Path

try:
    from .connection import get_container_manager, DockerConnectionError
    from ..config import get_config
    from ..models import PDG, MethodPDG, PDGNode, PDGEdge, EdgeType, NodeType
except ImportError:
    from client.connection import get_container_manager, DockerConnectionError
    from config import get_config
    from models import PDG, MethodPDG, PDGNode, PDGEdge, EdgeType, NodeType

logger = logging.getLogger(__name__)


class JoernClient:
    """
    Client for interacting with Joern
    """
    
    def __init__(self, auto_start: bool = True):
        self.config = get_config()
        self.container = get_container_manager()
        
        if auto_start:
            self.ensure_container_running()
    
    def ensure_container_running(self) -> bool:
        """Ensure container is running"""
        if not self.container.is_container_running():
            logger.info("Starting Joern container...")
            return self.container.start_container()
        return True
    
    def parse_code(
        self, 
        code: str, 
        language: str = "python",
        output_name: str = "code"
    ) -> Optional[str]:
        """Parse code and create CPG"""
        self.ensure_container_running()
        
        ext = self._get_extension(language)
        
        local_file = self.config.paths.workspace_dir / f"{output_name}{ext}"
        local_file.write_text(code)
        
        container_input = f"/workspace/{output_name}{ext}"
        container_output = f"/workspace/{output_name}.cpg"
        
        logger.info(f"Parsing code with Joern ({language})...")
        
        cmd = [
            "joern-parse",
            container_input,
            "--output", container_output
        ]
        
        returncode, stdout, stderr = self.container.execute_command(
            cmd,
            timeout=self.config.docker.parse_timeout
        )
        
        if returncode != 0:
            logger.error(f"joern-parse failed: {stderr}")
            return None
        
        logger.info(f"CPG created: {container_output}")
        return container_output
    
    def parse_file(self, file_path: str, output_name: str = None) -> Optional[str]:
        """Parse a file and create CPG"""
        self.ensure_container_running()
        
        file_path = Path(file_path)
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return None
        
        code = file_path.read_text()
        language = self.config.get_language_from_extension(str(file_path))
        output_name = output_name or file_path.stem
        
        return self.parse_code(code, language, output_name)
    
    def extract_pdg(self, cpg_path: str) -> Optional[PDG]:
        """Extract PDG from a CPG"""
        self.ensure_container_running()
        
        query = self._get_pdg_extraction_query()
        
        returncode, stdout, stderr = self._run_joern_query(cpg_path, query)
        
        if returncode != 0:
            logger.error(f"PDG extraction failed: {stderr}")
            return None
        
        return self._parse_pdg_output(stdout)
    
    def extract_pdg_from_code(
        self, 
        code: str, 
        language: str = "python"
    ) -> Optional[PDG]:
        """Extract PDG directly from code"""
        cpg_path = self.parse_code(code, language, "temp_code")
        
        if not cpg_path:
            return None
        
        return self.extract_pdg(cpg_path)
    
    def get_methods(self, cpg_path: str) -> List[str]:
        """Get list of method names from CPG"""
        query = 'cpg.method.name.l.foreach(println)'
        
        returncode, stdout, stderr = self._run_joern_query(cpg_path, query)
        
        if returncode != 0:
            return []
        
        methods = []
        for line in stdout.strip().split('\n'):
            line = line.strip()
            if line and not line.startswith(('val ', 'joern>', 'Warning')):
                methods.append(line)
        
        return methods
    
    def get_method_pdg_dot(self, cpg_path: str, method_name: str) -> Optional[str]:
        """Get PDG in DOT format for a specific method"""
        query = f'cpg.method.name("{method_name}").dotPdg.l.foreach(println)'
        
        returncode, stdout, stderr = self._run_joern_query(cpg_path, query)
        
        if returncode != 0:
            return None
        
        return stdout
    
    def _run_joern_query(
        self, 
        cpg_path: str, 
        query: str
    ) -> tuple:
        """Run a Joern query on a CPG"""
        script = f'''
importCpg("{cpg_path}")
{query}
'''
        
        script_file = self.config.paths.workspace_dir / "temp_query.sc"
        script_file.write_text(script)
        
        cmd = [
            "joern",
            "--script", "/workspace/temp_query.sc"
        ]
        
        return self.container.execute_command(
            cmd,
            timeout=self.config.docker.query_timeout
        )
    
    def _get_pdg_extraction_query(self) -> str:
            """Get Joern query for PDG extraction - filters internal methods"""
            return '''
cpg.method.l.filter { method =>
    // Filter out internal/built-in methods
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
    
    // Extract all AST nodes
    method.ast.l.foreach { node =>
        val line = scala.util.Try(node.lineNumber.getOrElse(-1)).getOrElse(-1)
        val code = scala.util.Try(node.code).getOrElse("").replace("\\n", " ").replace("|", " ").take(200)
        val label = scala.util.Try(node.label).getOrElse("UNKNOWN")
        println(s"NODE|${node.id}|${label}|${code}|${line}")
    }
    
    // Extract control flow using out edges
    scala.util.Try {
        method.ast.l.foreach { node =>
            scala.util.Try {
                node.out("CDG").l.foreach { target =>
                    println(s"CDG|${node.id}|${target.id}")
                }
            }
        }
    }
    
    // Extract data flow using out edges
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
        """Parse Joern output into PDG object"""
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
                        code=parts[3],
                        line_number=int(parts[4]) if parts[4] != '-1' else None,
                        node_type=self._map_node_type(parts[2]),
                        method_name=current_method.method_name
                    )
                    current_method.add_node(node)
                    
            elif line.startswith('CDG|') and current_method:
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
        mapping = {
            'METHOD': NodeType.METHOD,
            'PARAM': NodeType.PARAMETER,
            'LOCAL': NodeType.LOCAL,
            'LITERAL': NodeType.LITERAL,
            'IDENTIFIER': NodeType.IDENTIFIER,
            'CALL': NodeType.CALL,
            'RETURN': NodeType.RETURN,
            'CONTROL_STRUCTURE': NodeType.CONTROL_STRUCTURE,
            'BLOCK': NodeType.BLOCK,
        }
        return mapping.get(label, NodeType.UNKNOWN)
    
    def _get_extension(self, language: str) -> str:
        """Get file extension for language"""
        extensions = {
            'python': '.py',
            'java': '.java',
            'javascript': '.js',
            'c': '.c',
            'cpp': '.cpp',
            'go': '.go'
        }
        return extensions.get(language.lower(), '.txt')
    
    def cleanup(self):
        """Clean up temporary files"""
        workspace = self.config.paths.workspace_dir
        
        for pattern in ['temp_*.py', 'temp_*.cpg', 'temp_*.sc']:
            for f in workspace.glob(pattern):
                try:
                    f.unlink()
                except Exception:
                    pass
    
    def __enter__(self):
        """Context manager entry"""
        self.ensure_container_running()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()