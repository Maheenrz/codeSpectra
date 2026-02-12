# detectors/type4/joern/client/connection.py

"""
Docker connection manager for Joern container
"""

import subprocess
import time
import logging
from typing import Optional, Tuple
from pathlib import Path

try:
    from ..config import get_config, get_docker_config
except ImportError:
    from config import get_config, get_docker_config
logger = logging.getLogger(__name__)


class DockerConnectionError(Exception):
    """Exception for Docker connection issues"""
    pass


class JoernContainerManager:
    """
    Manages the Joern Docker container lifecycle
    """
    
    def __init__(self):
        self.config = get_config()
        self.docker_config = get_docker_config()
        self.container_name = self.docker_config.container_name
        self.image_name = self.docker_config.image_name
        
    def is_docker_available(self) -> bool:
        """Check if Docker is available on the system"""
        try:
            result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def is_container_running(self) -> bool:
        """Check if Joern container is currently running"""
        try:
            result = subprocess.run(
                ["docker", "ps", "-q", "-f", f"name={self.container_name}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return bool(result.stdout.strip())
        except Exception as e:
            logger.error(f"Error checking container status: {e}")
            return False
    
    def container_exists(self) -> bool:
        """Check if container exists (running or stopped)"""
        try:
            result = subprocess.run(
                ["docker", "ps", "-aq", "-f", f"name={self.container_name}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return bool(result.stdout.strip())
        except Exception:
            return False
    
    def start_container(self) -> bool:
        """Start the Joern container"""
        if not self.is_docker_available():
            raise DockerConnectionError("Docker is not available. Please start Docker.")
        
        if self.is_container_running():
            logger.info(f"Container '{self.container_name}' is already running")
            return True
        
        if self.container_exists():
            logger.info(f"Starting existing container '{self.container_name}'...")
            try:
                result = subprocess.run(
                    ["docker", "start", self.container_name],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    logger.info("Container started successfully")
                    return True
                else:
                    logger.error(f"Failed to start container: {result.stderr}")
                    return False
            except Exception as e:
                logger.error(f"Error starting container: {e}")
                return False
        
        logger.info(f"Creating new container '{self.container_name}'...")
        
        workspace_path = self.config.paths.workspace_dir
        output_path = self.config.paths.output_dir
        
        try:
            cmd = [
                "docker", "run", "-d",
                "--name", self.container_name,
                "-v", f"{workspace_path}:/workspace",
                "-v", f"{output_path}:/output",
                self.image_name
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info("Container created and started successfully")
                time.sleep(2)
                return True
            else:
                logger.error(f"Failed to create container: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Timeout creating container")
            return False
        except Exception as e:
            logger.error(f"Error creating container: {e}")
            return False
    
    def stop_container(self) -> bool:
        """Stop the Joern container"""
        if not self.is_container_running():
            logger.info("Container is not running")
            return True
        
        logger.info(f"Stopping container '{self.container_name}'...")
        
        try:
            result = subprocess.run(
                ["docker", "stop", self.container_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info("Container stopped successfully")
                return True
            else:
                logger.error(f"Failed to stop container: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error stopping container: {e}")
            return False
    
    def remove_container(self) -> bool:
        """Remove the Joern container"""
        self.stop_container()
        
        if not self.container_exists():
            return True
        
        logger.info(f"Removing container '{self.container_name}'...")
        
        try:
            result = subprocess.run(
                ["docker", "rm", "-f", self.container_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error removing container: {e}")
            return False
    
    def execute_command(
        self, 
        command: list, 
        timeout: int = None,
        capture_output: bool = True
    ) -> Tuple[int, str, str]:
        """Execute a command inside the Joern container"""
        if not self.is_container_running():
            if not self.start_container():
                raise DockerConnectionError("Failed to start Joern container")
        
        timeout = timeout or self.docker_config.query_timeout
        
        docker_cmd = ["docker", "exec", self.container_name] + command
        
        try:
            result = subprocess.run(
                docker_cmd,
                capture_output=capture_output,
                text=True,
                timeout=timeout
            )
            
            return result.returncode, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out after {timeout}s: {' '.join(command)}")
            return -1, "", "Command timed out"
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return -1, "", str(e)
    
    def execute_joern_command(
        self, 
        joern_command: str, 
        cpg_path: str = None,
        timeout: int = None
    ) -> Tuple[int, str, str]:
        """Execute a Joern query command"""
        timeout = timeout or self.docker_config.query_timeout
        
        if cpg_path:
            cmd = [
                "joern",
                "--script", "-",
                "--param", f"cpgFile={cpg_path}"
            ]
        else:
            cmd = ["joern", "--script", "-"]
        
        docker_cmd = ["docker", "exec", "-i", self.container_name] + cmd
        
        try:
            result = subprocess.run(
                docker_cmd,
                input=joern_command,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return result.returncode, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            return -1, "", "Joern command timed out"
        except Exception as e:
            return -1, "", str(e)
    
    def copy_to_container(self, local_path: str, container_path: str) -> bool:
        """Copy file from host to container"""
        try:
            result = subprocess.run(
                ["docker", "cp", local_path, f"{self.container_name}:{container_path}"],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error copying to container: {e}")
            return False
    
    def copy_from_container(self, container_path: str, local_path: str) -> bool:
        """Copy file from container to host"""
        try:
            result = subprocess.run(
                ["docker", "cp", f"{self.container_name}:{container_path}", local_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error copying from container: {e}")
            return False
    
    def get_container_info(self) -> dict:
        """Get information about the container"""
        return {
            "name": self.container_name,
            "image": self.image_name,
            "running": self.is_container_running(),
            "exists": self.container_exists(),
            "docker_available": self.is_docker_available()
        }


_container_manager: Optional[JoernContainerManager] = None


def get_container_manager() -> JoernContainerManager:
    """Get the singleton container manager instance"""
    global _container_manager
    if _container_manager is None:
        _container_manager = JoernContainerManager()
    return _container_manager