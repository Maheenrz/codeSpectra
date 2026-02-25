# detectors/type4/joern/config.py

"""
Configuration for Joern Type-4 Semantic Clone Detection

This detector focuses ONLY on Type-4 (semantic) clones.
Type-1, Type-2, Type-3 are handled by other detectors in CodeSpectra.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict


# Base directory
BASE_DIR = Path(__file__).parent


@dataclass
class DockerConfig:
    """Docker container configuration"""
    
    image_name: str = "codespectra-joern:latest"
    container_name: str = "codespectra-joern"
    
    # Paths inside container
    workspace_path: str = "/workspace"
    output_path: str = "/output"
    
    # Resource limits
    memory_limit: str = "4g"
    
    # Timeouts (seconds)
    start_timeout: int = 60
    query_timeout: int = 120
    parse_timeout: int = 300


@dataclass
class JoernConfig:
    """Joern tool configuration"""
    
    joern_cli: str = "joern"
    joern_parse: str = "joern-parse"
    joern_export: str = "joern-export"
    
    # All supported languages for Type-4 detection
    supported_languages: List[str] = field(default_factory=lambda: [
        "python",
        "java", 
        "javascript",
        "c",
        "cpp",
        "go",
        "php"
    ])
    
    # Language file extensions
    language_extensions: Dict[str, List[str]] = field(default_factory=lambda: {
        "python": [".py"],
        "java": [".java"],
        "javascript": [".js", ".jsx", ".mjs"],
        "typescript": [".ts", ".tsx"],
        "c": [".c", ".h"],
        "cpp": [".cpp", ".cc", ".cxx", ".hpp", ".hh", ".h++"],
        "go": [".go"],
        "php": [".php"]
    })
    
    # Joern language identifiers
    joern_language_names: Dict[str, str] = field(default_factory=lambda: {
        "python": "pythonsrc",
        "java": "javasrc",
        "javascript": "jssrc",
        "typescript": "jssrc",
        "c": "c",
        "cpp": "cpp",
        "go": "golang",
        "php": "php"
    })


@dataclass
class SemanticConfig:
    """Type-4 Semantic Clone Detection Configuration"""
    
    # Main threshold for semantic clone detection
    # Code pairs with similarity >= this threshold are semantic clones
    semantic_clone_threshold: float = 0.55
    
    # High confidence threshold
    high_confidence_threshold: float = 0.75
    
    # Weights for semantic similarity calculation
    # These are optimized for TYPE-4 (behavioral) detection
    weights: Dict[str, float] = field(default_factory=lambda: {
        "node_type_similarity": 0.15,      # What operations exist
        "control_flow_similarity": 0.35,   # How control flows
        "data_flow_similarity": 0.40,      # How data flows (MOST IMPORTANT)
        "structural_similarity": 0.10      # Overall graph shape
    })
    
    # Language-specific threshold adjustments
    # Some languages need different thresholds due to syntax differences
    language_threshold_adjustments: Dict[str, float] = field(default_factory=lambda: {
        "python": 0.0,      # Base threshold
        "java": 0.0,        # Base threshold
        "javascript": -0.05, # Slightly lower (more dynamic)
        "c": 0.05,          # Slightly higher (more structured)
        "cpp": 0.05,        # Slightly higher (more structured)
        "go": 0.0,          # Base threshold
        "php": -0.05        # Slightly lower
    })


@dataclass 
class PathConfig:
    """Path configuration"""
    
    docker_dir: Path = None
    workspace_dir: Path = None
    output_dir: Path = None
    
    def __post_init__(self):
        self.docker_dir = BASE_DIR / "docker"
        self.workspace_dir = BASE_DIR / "docker" / "workspace"
        self.output_dir = BASE_DIR / "docker" / "output"
        
        # Create directories
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)


class Config:
    """Main configuration - Type-4 focused"""
    
    def __init__(self):
        self.docker = DockerConfig()
        self.joern = JoernConfig()
        self.semantic = SemanticConfig()
        self.paths = PathConfig()
    
    def get_language_from_extension(self, file_path: str) -> Optional[str]:
        """Detect language from file extension"""
        ext = Path(file_path).suffix.lower()
        
        for language, extensions in self.joern.language_extensions.items():
            if ext in extensions:
                return language
        return None
    
    def get_joern_language(self, language: str) -> str:
        """Get Joern's language identifier"""
        return self.joern.joern_language_names.get(language.lower(), "pythonsrc")
    
    def is_language_supported(self, language: str) -> bool:
        """Check if language is supported"""
        return language.lower() in self.joern.supported_languages
    
    def get_threshold_for_language(self, language: str) -> float:
        """Get adjusted threshold for specific language"""
        base = self.semantic.semantic_clone_threshold
        adjustment = self.semantic.language_threshold_adjustments.get(language.lower(), 0.0)
        return base + adjustment


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get global config instance"""
    global _config
    if _config is None:
        _config = Config()
    return _config


def get_docker_config() -> DockerConfig:
    return get_config().docker


def get_joern_config() -> JoernConfig:
    return get_config().joern


def get_semantic_config() -> SemanticConfig:
    return get_config().semantic