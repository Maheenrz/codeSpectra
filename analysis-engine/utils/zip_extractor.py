"""
ZIP Extractor
=============
Handles nested zip uploads for class-wide analysis.

Supported structures:

  Structure A — class zip of student zips:
    assignment.zip
    ├── alice.zip        ← student name = zip filename
    │   ├── q1.cpp
    │   └── project/
    │       └── main.cpp
    └── bob.zip
        └── solution.cpp

  Structure B — class zip of student folders:
    assignment.zip
    ├── alice/
    │   └── q1.cpp
    └── bob/
        └── solution.cpp

  Structure C — single project zip (intra-project detection):
    project.zip
    ├── src/
    │   ├── UserController.java
    │   └── OrderService.java
    └── models/
        └── Cart.java
"""

from __future__ import annotations
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
        self._tmp_dirs: List[str] = []   # cleanup later

    def extract(
        self,
        zip_path: str,
    ) -> Tuple[str, Dict[str, List[str]]]:
        """
        Extract the zip and detect its structure.

        Returns:
            (mode, data)
            mode = "class"   → data = {student_name: [abs_file_paths]}
            mode = "project" → data = {"project": [abs_file_paths]}
        """
        tmp = tempfile.mkdtemp(prefix="codespectra_zip_")
        self._tmp_dirs.append(tmp)
        root = Path(tmp)

        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(root)

        # Remove macOS __MACOSX artifacts
        self._clean_macos(root)

        return self._detect_and_map(root)

    def cleanup(self) -> None:
        """Delete all temporary directories created by this instance."""
        for d in self._tmp_dirs:
            shutil.rmtree(d, ignore_errors=True)
        self._tmp_dirs.clear()

    # ── Detection logic ───────────────────────────────────────────────────────

    def _detect_and_map(
        self, root: Path
    ) -> Tuple[str, Dict[str, List[str]]]:

        top_entries = [p for p in root.iterdir()
                       if not p.name.startswith(".")]

        # ── Structure A: top-level zip files ──────────────────────────────
        zip_entries = [p for p in top_entries if p.suffix == ".zip"]
        if len(zip_entries) >= 2:
            student_map: Dict[str, List[str]] = {}
            for zp in zip_entries:
                student_name = zp.stem
                sub_tmp      = Path(tempfile.mkdtemp(prefix=f"cs_{student_name}_"))
                self._tmp_dirs.append(str(sub_tmp))
                with zipfile.ZipFile(zp, "r") as zf:
                    zf.extractall(sub_tmp)
                self._clean_macos(sub_tmp)
                files = _collect_code_files(sub_tmp)
                if files:
                    student_map[student_name] = files
            if student_map:
                return "class", student_map

        # ── Structure B: top-level directories (one per student) ──────────
        dir_entries = [p for p in top_entries if p.is_dir()]
        if len(dir_entries) >= 2:
            # Check each dir has code files
            student_map = {}
            for d in dir_entries:
                files = _collect_code_files(d)
                if files:
                    student_map[d.name] = files
            if len(student_map) >= 2:
                return "class", student_map

        # ── Structure C: flat zip or single project ────────────────────────
        all_files = _collect_code_files(root)
        return "project", {"project": all_files}

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _clean_macos(root: Path) -> None:
        macos = root / "__MACOSX"
        if macos.exists():
            shutil.rmtree(macos)
        for ds in root.rglob(".DS_Store"):
            ds.unlink(missing_ok=True)