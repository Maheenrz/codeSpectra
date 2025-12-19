"""
File Upload Service
Handles file/zip uploads, extraction, and multi-language processing
"""

import os
import zipfile
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import hashlib
import magic  # For file type detection


@dataclass
class UploadedFile:
    """Represents an uploaded file"""
    file_id: int
    original_name: str
    file_path: str
    file_type: str  # python, java, cpp, c, javascript
    file_size: int
    content_hash: str
    lines_of_code: int
    language: str


class LanguageDetector:
    """Detect programming language from file extension"""
    
    LANGUAGE_MAP = {
        '.py': 'python',
        '.java': 'java',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.c': 'c',
        '.h': 'c',
        '.hpp': 'cpp',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.cs': 'csharp',
        '.php': 'php',
        '.rb': 'ruby',
        '.go': 'go',
        '.rs': 'rust',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
    }
    
    @classmethod
    def detect(cls, file_path: str) -> Optional[str]:
        """Detect language from file extension"""
        ext = Path(file_path).suffix.lower()
        return cls.LANGUAGE_MAP.get(ext)
    
    @classmethod
    def is_supported(cls, file_path: str) -> bool:
        """Check if file type is supported"""
        return cls.detect(file_path) is not None
    
    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        """Get list of supported file extensions"""
        return list(cls.LANGUAGE_MAP.keys())


class FileUploadService:
    """Service for handling file uploads and extraction"""
    
    def __init__(self, upload_dir: str = "./data/uploads", temp_dir: str = "./data/temp"):
        self.upload_dir = Path(upload_dir)
        self.temp_dir = Path(temp_dir)
        self.extracted_dir = Path("./data/extracted")
        
        # Create directories if they don't exist
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.extracted_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration
        self.max_file_size = 10 * 1024 * 1024  # 10 MB
        self.max_zip_size = 100 * 1024 * 1024  # 100 MB
        self.max_files = 1000
        
        # Ignored directories
        self.ignored_dirs = {
            '__pycache__', 'node_modules', '.git', '.svn', 
            'venv', '.venv', 'env', 'build', 'dist',
            'target', 'bin', 'obj', '.idea', '.vscode'
        }
        
        # Ignored files
        self.ignored_files = {
            '.pyc', '.pyo', '.class', '.o', '.so', '.dll',
            '.exe', '.jar', '.war', '.ear'
        }
    
    async def process_upload(
        self,
        files: List[Any],  # FastAPI UploadFile objects
        project_id: int,
        user_id: int
    ) -> Tuple[List[UploadedFile], Dict[str, int]]:
        """
        Process uploaded files (single files or ZIP)
        
        Args:
            files: List of uploaded files
            project_id: Project ID for organizing files
            user_id: User ID who uploaded
            
        Returns:
            Tuple of (processed files, statistics)
        """
        processed_files = []
        stats = {
            'total_uploaded': len(files),
            'processed': 0,
            'skipped': 0,
            'errors': 0,
            'languages': {}
        }
        
        for uploaded_file in files:
            try:
                # Check if it's a ZIP file
                if uploaded_file.filename.endswith('.zip'):
                    # Process ZIP file
                    zip_files = await self._process_zip(uploaded_file, project_id)
                    processed_files.extend(zip_files)
                    stats['processed'] += len(zip_files)
                else:
                    # Process single file
                    processed_file = await self._process_single_file(
                        uploaded_file, 
                        project_id
                    )
                    
                    if processed_file:
                        processed_files.append(processed_file)
                        stats['processed'] += 1
                    else:
                        stats['skipped'] += 1
                        
            except Exception as e:
                print(f"Error processing {uploaded_file.filename}: {e}")
                stats['errors'] += 1
        
        # Update language statistics
        for file in processed_files:
            lang = file.language
            stats['languages'][lang] = stats['languages'].get(lang, 0) + 1
        
        return processed_files, stats
    
    async def _process_single_file(
        self,
        uploaded_file: Any,
        project_id: int
    ) -> Optional[UploadedFile]:
        """Process a single uploaded file"""
        
        # Check file size
        content = await uploaded_file.read()
        if len(content) > self.max_file_size:
            print(f"File {uploaded_file.filename} too large: {len(content)} bytes")
            return None
        
        # Check if supported language
        language = LanguageDetector.detect(uploaded_file.filename)
        if not language:
            print(f"Unsupported file type: {uploaded_file.filename}")
            return None
        
        # Create project directory
        project_dir = self.upload_dir / str(project_id)
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = project_dir / uploaded_file.filename
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Calculate metadata
        content_text = content.decode('utf-8', errors='ignore')
        lines_of_code = len([line for line in content_text.split('\n') if line.strip()])
        content_hash = hashlib.sha256(content).hexdigest()
        
        return UploadedFile(
            file_id=0,  # Will be set when saved to database
            original_name=uploaded_file.filename,
            file_path=str(file_path),
            file_type=Path(uploaded_file.filename).suffix[1:],  # Remove dot
            file_size=len(content),
            content_hash=content_hash,
            lines_of_code=lines_of_code,
            language=language
        )
    
    async def _process_zip(
        self,
        uploaded_file: Any,
        project_id: int
    ) -> List[UploadedFile]:
        """Extract and process ZIP file"""
        
        # Save ZIP temporarily
        zip_content = await uploaded_file.read()
        
        if len(zip_content) > self.max_zip_size:
            raise ValueError(f"ZIP file too large: {len(zip_content)} bytes")
        
        temp_zip_path = self.temp_dir / f"temp_{project_id}.zip"
        with open(temp_zip_path, 'wb') as f:
            f.write(zip_content)
        
        # Extract ZIP
        extract_dir = self.extracted_dir / str(project_id)
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        except zipfile.BadZipFile:
            raise ValueError("Invalid ZIP file")
        finally:
            # Clean up temp ZIP
            if temp_zip_path.exists():
                temp_zip_path.unlink()
        
        # Scan extracted files
        processed_files = []
        file_count = 0
        
        for root, dirs, files in os.walk(extract_dir):
            # Remove ignored directories
            dirs[:] = [d for d in dirs if d not in self.ignored_dirs]
            
            for filename in files:
                if file_count >= self.max_files:
                    print(f"Maximum file limit reached: {self.max_files}")
                    break
                
                # Skip ignored files
                if Path(filename).suffix in self.ignored_files:
                    continue
                
                file_path = Path(root) / filename
                
                # Check if supported language
                language = LanguageDetector.detect(str(file_path))
                if not language:
                    continue
                
                try:
                    # Read file
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    
                    # Check size
                    if len(content) > self.max_file_size:
                        continue
                    
                    # Calculate metadata
                    content_text = content.decode('utf-8', errors='ignore')
                    lines_of_code = len([line for line in content_text.split('\n') if line.strip()])
                    content_hash = hashlib.sha256(content).hexdigest()
                    
                    # Get relative path within project
                    relative_path = file_path.relative_to(extract_dir)
                    
                    processed_file = UploadedFile(
                        file_id=0,
                        original_name=str(relative_path),
                        file_path=str(file_path),
                        file_type=file_path.suffix[1:],
                        file_size=len(content),
                        content_hash=content_hash,
                        lines_of_code=lines_of_code,
                        language=language
                    )
                    
                    processed_files.append(processed_file)
                    file_count += 1
                    
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
                    continue
        
        return processed_files
    
    def chunk_large_file(self, file_path: str, max_lines: int = 10000) -> List[str]:
        """
        Split large files into chunks for processing
        
        Args:
            file_path: Path to file
            max_lines: Maximum lines per chunk
            
        Returns:
            List of chunk file paths
        """
        chunks = []
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        if len(lines) <= max_lines:
            return [file_path]  # No need to chunk
        
        # Create chunks
        file_path_obj = Path(file_path)
        chunk_dir = file_path_obj.parent / "chunks"
        chunk_dir.mkdir(exist_ok=True)
        
        for i in range(0, len(lines), max_lines):
            chunk_lines = lines[i:i + max_lines]
            chunk_path = chunk_dir / f"{file_path_obj.stem}_chunk_{i // max_lines}{file_path_obj.suffix}"
            
            with open(chunk_path, 'w', encoding='utf-8') as f:
                f.writelines(chunk_lines)
            
            chunks.append(str(chunk_path))
        
        return chunks
    
    def cleanup_project(self, project_id: int):
        """Clean up all files for a project"""
        project_dir = self.upload_dir / str(project_id)
        extracted_dir = self.extracted_dir / str(project_id)
        
        if project_dir.exists():
            shutil.rmtree(project_dir)
        
        if extracted_dir.exists():
            shutil.rmtree(extracted_dir)
    
    def get_file_statistics(self, files: List[UploadedFile]) -> Dict[str, Any]:
        """Get statistics about uploaded files"""
        stats = {
            'total_files': len(files),
            'total_size': sum(f.file_size for f in files),
            'total_lines': sum(f.lines_of_code for f in files),
            'languages': {},
            'file_types': {}
        }
        
        for file in files:
            # Language stats
            lang = file.language
            if lang not in stats['languages']:
                stats['languages'][lang] = {
                    'count': 0,
                    'lines': 0,
                    'size': 0
                }
            
            stats['languages'][lang]['count'] += 1
            stats['languages'][lang]['lines'] += file.lines_of_code
            stats['languages'][lang]['size'] += file.file_size
            
            # File type stats
            file_type = file.file_type
            stats['file_types'][file_type] = stats['file_types'].get(file_type, 0) + 1
        
        return stats


# Example usage
async def example_usage():
    """Example of how to use the upload service"""
    from fastapi import UploadFile
    
    upload_service = FileUploadService()
    
    # Simulated uploaded files
    files = []  # List of UploadFile objects from FastAPI
    
    # Process uploads
    processed_files, stats = await upload_service.process_upload(
        files=files,
        project_id=1,
        user_id=1
    )
    
    print(f"Processed {stats['processed']} files")
    print(f"Languages: {stats['languages']}")
    
    # Get statistics
    file_stats = upload_service.get_file_statistics(processed_files)
    print(f"Total lines of code: {file_stats['total_lines']}")
    
    # Cleanup when done
    # upload_service.cleanup_project(project_id=1)


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())