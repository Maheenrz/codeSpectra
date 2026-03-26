# analysis-engine/utils/zip_extractor.py
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List, Tuple

_CODE_EXTS = {
    ".cpp", ".c", ".h", ".hpp", ".cc", ".cxx",
    ".java", ".py",
    ".js", ".jsx", ".ts", ".tsx",
}

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
        tmp = tempfile.mkdtemp(prefix="codespectra_zip_")
        self._tmp_dirs.append(tmp)
        root = Path(tmp)

        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(root)

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
        for item in list(current_path.rglob("*.zip")):
            # Create a folder with the same name as the zip
            extract_to = item.parent / item.stem
            try:
                with zipfile.ZipFile(item, 'r') as zf:
                    zf.extractall(extract_to)
                item.unlink()  # Remove the zip after extraction
                self._recursive_unzip(extract_to) # Search inside the new folder
            except zipfile.BadZipFile:
                continue

    def _detect_and_map(self, root: Path) -> Tuple[str, Dict[str, List[str]]]:
        # Filter out hidden files
        top_entries = [p for p in root.iterdir() if not p.name.startswith(".")]

        # ── Structure A: Check for sub-directories (resulting from nested zips or folders) ──
        dir_entries = [p for p in top_entries if p.is_dir()]
        
        if len(dir_entries) >= 2:
            student_map: Dict[str, List[str]] = {}
            for d in dir_entries:
                files = _collect_code_files(d)
                if files:
                    student_map[d.name] = files
            
            if len(student_map) >= 2:
                return "class", student_map

        # ── Structure B: Single project / Flat zip ────────────────────────
        all_files = _collect_code_files(root)
        return "project", {"project": all_files}

    @staticmethod
    def _clean_macos(root: Path) -> None:
        macos = root / "__MACOSX"
        if macos.exists():
            shutil.rmtree(macos)
        for ds in root.rglob(".DS_Store"):
            ds.unlink(missing_ok=True)