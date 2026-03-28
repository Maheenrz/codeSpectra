# analysis-engine/utils/zip_extractor.py

import os
import shutil
import tempfile
import zipfile
import logging
from pathlib import Path
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

# Header files (.h/.hpp/.hxx) have extension_weight=0.0 in the Type-3 config,
# meaning they are excluded from structural comparison. We also exclude them
# from ZIP collection so they never reach Type-1 or Type-2 detectors either.
# Only include implementation files.
_CODE_EXTS = {
    ".cpp", ".c", ".cc", ".cxx",   # C/C++ implementation
    ".java",                          # Java
    ".py",                            # Python
    ".js", ".jsx", ".ts", ".tsx",   # JavaScript / TypeScript
}
# Header/interface files are intentionally excluded:
# ".h", ".hpp", ".hxx" — always boilerplate, cause false positives

def _is_code(path: Path) -> bool:
    return path.suffix.lower() in _CODE_EXTS

def _collect_code_files(root: Path) -> List[str]:
    """Recursively collect all code files under root."""
    found = []
    for p in root.rglob("*"):
        if p.is_file() and _is_code(p):
            found.append(str(p))
    return sorted(found)

class ZipExtractor:
    """
    Extracts a zip upload and returns either:
      - student_map: {student_name: [file_paths]}  (multi-student mode)
      - file_paths:  [file_paths]                  (single-project mode)
    """

    def __init__(self):
        self._tmp_dirs: List[str] = []   # for cleanup later

    def extract(self, zip_path: str) -> Tuple[str, Dict[str, List[str]]]:
        """
        Extract the zip and detect its structure.
        Returns: (mode, data)
        """
        logger.info(f"Extracting ZIP: {zip_path}")
        tmp = tempfile.mkdtemp(prefix="codespectra_zip_")
        self._tmp_dirs.append(tmp)
        root = Path(tmp)

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(root)
            logger.info(f"Extracted to {root}")
            
            # Log extracted contents
            all_items = list(root.rglob("*"))
            logger.info(f"Extracted {len(all_items)} total items")
            
            code_files = [p for p in all_items if p.is_file() and _is_code(p)]
            logger.info(f"Found {len(code_files)} code files")
            
        except Exception as e:
            logger.error(f"Failed to extract ZIP: {e}")
            raise

        # Remove macOS artifacts immediately
        self._clean_macos(root)
        
        # Handle nested zips before detection
        self._recursive_unzip(root)

        return self._detect_and_map(root)

    def cleanup(self) -> None:
        """Delete all temporary directories created by this instance."""
        for d in self._tmp_dirs:
            shutil.rmtree(d, ignore_errors=True)
        self._tmp_dirs.clear()

    def _recursive_unzip(self, current_path: Path):
        """Recursively find and extract nested zip files."""
        zip_files = list(current_path.rglob("*.zip"))
        logger.info(f"Found {len(zip_files)} nested zip files")
        
        for item in zip_files:
            # Create a folder with the same name as the zip
            extract_to = item.parent / item.stem
            try:
                logger.info(f"Extracting nested zip: {item.name} to {extract_to}")
                with zipfile.ZipFile(item, 'r') as zf:
                    zf.extractall(extract_to)
                item.unlink()  # Remove the zip after extraction
                self._recursive_unzip(extract_to)  # Search inside the new folder
            except zipfile.BadZipFile:
                logger.warning(f"Bad zip file: {item}")
                continue

    def _detect_and_map(self, root: Path) -> Tuple[str, Dict[str, List[str]]]:
        # Filter out hidden files
        top_entries = [p for p in root.iterdir() if not p.name.startswith(".")]
        logger.info(f"Top-level entries: {[e.name for e in top_entries]}")
        
        # ── Structure A: Check for sub-directories (resulting from nested zips or folders) ──
        dir_entries = [p for p in top_entries if p.is_dir()]
        
        if len(dir_entries) >= 2:
            logger.info(f"Detected multi-student mode with {len(dir_entries)} directories")
            student_map: Dict[str, List[str]] = {}
            for d in dir_entries:
                files = _collect_code_files(d)
                if files:
                    student_map[d.name] = files
                    logger.info(f"  Student '{d.name}': {len(files)} files")
                else:
                    logger.warning(f"  Student '{d.name}': No code files found")
            
            if len(student_map) >= 2:
                logger.info(f"Returning class mode with {len(student_map)} students")
                return "class", student_map
            else:
                logger.warning(f"Only {len(student_map)} students with files, falling back to project mode")

        # ── Structure B: Single project / Flat zip ────────────────────────
        all_files = _collect_code_files(root)
        logger.info(f"Detected project mode with {len(all_files)} files")
        return "project", {"project": all_files}

    @staticmethod
    def _clean_macos(root: Path) -> None:
        macos = root / "__MACOSX"
        if macos.exists():
            shutil.rmtree(macos)
        for ds in root.rglob(".DS_Store"):
            ds.unlink(missing_ok=True)