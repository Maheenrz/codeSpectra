# """
# CodeSpectra Analysis Engine - Project Level Type 1 Clone Detection
# Handles ZIP uploads, folder structures, and multi-language analysis
# """
# import os
# import time
# import zipfile
# import shutil
# from pathlib import Path
# from typing import List, Dict, Optional
# from dataclasses import dataclass
# from collections import defaultdict

# from fastapi import FastAPI, File, UploadFile
# from fastapi.responses import JSONResponse
# from fastapi.middleware.cors import CORSMiddleware

# # Import all Type 1 detectors
# from detectors.type1.hash_method import Type1HashMethod
# from detectors.type1.string_method import Type1StringMethod
# from detectors.type1.ast_exact_method import Type1ASTMethod

# app = FastAPI(title="CodeSpectra Analysis Engine", version="1.0.0")

# # CORS Configuration
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Configuration
# UPLOAD_DIR = Path("./data/uploads")
# UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# # Directories to ignore (junk folders)
# IGNORED_DIRS = {
#     'node_modules', 'venv', '.git', '__pycache__', '.idea', '.vscode',
#     'bin', 'obj', 'target', 'dist', 'build', '.vs', 'packages', 'Debug', 'Release'
# }

# # Files to ignore (non-code files)
# IGNORED_EXTS = {
#     '.json', '.md', '.txt', '.xml', '.html', '.css', '.gitignore',
#     '.sln', '.vcxproj', '.user', '.config', '.yml', '.yaml'
# }


# @dataclass
# class CodeFragment:
#     """Represents a code fragment (function, class, or block)"""
#     file_path: str      # Original file name
#     file_id: int        # Unique file identifier
#     start_line: int     # Starting line number
#     end_line: int       # Ending line number
#     content: str        # Actual code content
#     language: str       # Programming language
#     fragment_type: str  # 'function', 'class', 'block', 'whole_file'


# class LanguageDetector:
#     """Detects programming language from file extension"""
    
#     LANG_MAP = {
#         '.py': 'python',
#         '.java': 'java',
#         '.cpp': 'cpp', '.cc': 'cpp', '.cxx': 'cpp',
#         '.h': 'cpp', '.hpp': 'cpp', '.hxx': 'cpp',
#         '.c': 'c',
#         '.js': 'javascript', '.ts': 'typescript',
#         '.cs': 'csharp',
#         '.go': 'go',
#         '.rb': 'ruby',
#         '.php': 'php'
#     }
    
#     @classmethod
#     def detect(cls, filename: str) -> Optional[str]:
#         """Returns language or None"""
#         ext = Path(filename).suffix.lower()
#         return cls.LANG_MAP.get(ext)


# class FragmentExtractor:
#     """Extracts code fragments from files based on language"""
    
#     @staticmethod
#     def extract_python_fragments(file_path: Path, file_id: int, content: str) -> List[CodeFragment]:
#         """Extract functions and classes from Python using AST"""
#         import ast
#         import textwrap
        
#         fragments = []
#         try:
#             tree = ast.parse(content)
#             lines = content.splitlines(keepends=True)
            
#             for node in ast.walk(tree):
#                 if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
#                     start = node.lineno
#                     end = node.end_lineno or start
                    
#                     # Extract and dedent
#                     raw_chunk = "".join(lines[start-1:end])
#                     dedented = textwrap.dedent(raw_chunk)
                    
#                     frag_type = 'class' if isinstance(node, ast.ClassDef) else 'function'
                    
#                     fragments.append(CodeFragment(
#                         file_path=file_path.name,
#                         file_id=file_id,
#                         start_line=start,
#                         end_line=end,
#                         content=dedented,
#                         language='python',
#                         fragment_type=frag_type
#                     ))
            
#             # Fallback: if no functions/classes found, use whole file
#             if not fragments:
#                 fragments.append(CodeFragment(
#                     file_path=file_path.name,
#                     file_id=file_id,
#                     start_line=1,
#                     end_line=len(lines),
#                     content=content,
#                     language='python',
#                     fragment_type='whole_file'
#                 ))
                
#         except SyntaxError:
#             # If parse fails, treat as whole file (or empty if truly broken)
#             # We return empty list here to signal 'skipped' for now, or whole file if preferred
#             # Returning [] lets the main loop catch it as skipped.
#             print(f"⚠️ Syntax Error in {file_path.name}, skipping AST extraction.")
#             return []
        
#         return fragments
    
#     @staticmethod
#     def extract_blocks(file_path: Path, file_id: int, content: str, language: str) -> List[CodeFragment]:
#         """
#         Robust Stack-Based Block Extractor.
#         Captures nested blocks (like Java methods inside classes) 
#         and top-level blocks (like JS/C++ functions).
#         """
#         fragments = []
#         lines = content.splitlines()
#         stack = []  # Stores start lines of open braces
        
#         for i, line in enumerate(lines, 1):
#             stripped = line.strip()
            
#             # Skip comments to prevent fake brace detection
#             if stripped.startswith('//') or stripped.startswith('*') or stripped.startswith('/*'):
#                 continue
#             if language == 'python': # Just in case
#                 if stripped.startswith('#'): continue

#             # Push start line for every open brace
#             for char in line:
#                 if char == '{':
#                     stack.append(i)
#                 elif char == '}':
#                     if stack:
#                         start = stack.pop()
#                         end = i
                        
#                         # We found a block! Extract it.
#                         block_content = '\n'.join(lines[start-1:end])
                        
#                         # FILTER: Only keep "substantial" blocks (> 2 lines)
#                         # This ignores tiny blocks like "if(x){return;}" but keeps methods.
#                         if len(block_content.splitlines()) >= 3:
#                             fragments.append(CodeFragment(
#                                 file_path=file_path.name,
#                                 file_id=file_id,
#                                 start_line=start,
#                                 end_line=end,
#                                 content=block_content,
#                                 language=language,
#                                 fragment_type='block'
#                             ))
        
#         # Fallback: if no blocks found (e.g. file has no braces), use whole file
#         if not fragments:
#             fragments.append(CodeFragment(
#                 file_path=file_path.name,
#                 file_id=file_id,
#                 start_line=1,
#                 end_line=len(lines),
#                 content=content,
#                 language=language,
#                 fragment_type='whole_file'
#             ))
        
#         return fragments
    
#     @classmethod
#     def extract(cls, file_path: Path, file_id: int, language: str) -> List[CodeFragment]:
#         """Main extraction dispatcher"""
#         try:
#             with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
#                 content = f.read()
            
#             if not content.strip() or len(content) > 1_000_000:
#                 return []
            
#             if language == 'python':
#                 return cls.extract_python_fragments(file_path, file_id, content)
            
#             # UPDATED: Added javascript, typescript, go, php to block extraction
#             elif language in ['cpp', 'java', 'csharp', 'c', 'javascript', 'typescript', 'go', 'php', 'ruby']:
#                 return cls.extract_blocks(file_path, file_id, content, language)
            
#             else:
#                 # Generic: whole file
#                 return [CodeFragment(
#                     file_path=file_path.name,
#                     file_id=file_id,
#                     start_line=1,
#                     end_line=len(content.splitlines()),
#                     content=content,
#                     language=language,
#                     fragment_type='whole_file'
#                 )]
        
#         except Exception as e:
#             print(f"❌ Error extracting {file_path}: {e}")
#             return []


# def process_upload(file_path: Path, extract_root: Path) -> List[Path]:
#     """Handle ZIP extraction or single file"""
#     valid_files = []
    
#     if file_path.suffix == '.zip':
#         try:
#             with zipfile.ZipFile(file_path, 'r') as z:
#                 z.extractall(extract_root)
            
#             # Walk extracted directory
#             for root, dirs, files in os.walk(extract_root):
#                 # Filter out junk directories IN PLACE
#                 dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
                
#                 for file in files:
#                     full_path = Path(root) / file
#                     if full_path.suffix.lower() not in IGNORED_EXTS:
#                         if LanguageDetector.detect(file):
#                             valid_files.append(full_path)
        
#         except Exception as e:
#             print(f"❌ Error extracting ZIP: {e}")
    
#     elif LanguageDetector.detect(file_path.name):
#         valid_files.append(file_path)
    
#     return valid_files


# @app.get("/")
# def root():
#     return {
#         "status": "ok",
#         "message": "CodeSpectra Analysis Engine",
#         "version": "1.0.0",
#         "endpoints": ["/api/analyze", "/health"]
#     }


# @app.get("/health")
# def health():
#     return {"status": "healthy", "service": "analysis-engine"}


# @app.post("/api/analyze")
# async def analyze(files: List[UploadFile] = File(...)):
#     """
#     Main analysis endpoint
#     Accepts multiple files or ZIP archives
#     """
#     print(f"\n{'='*60}\n🚀 STARTING TYPE 1 CLONE ANALYSIS\n{'='*60}")
    
#     job_id = f"job_{int(time.time())}"
#     job_dir = UPLOAD_DIR / job_id
#     job_dir.mkdir(exist_ok=True)
    
#     # Step 1: Save and extract files
#     all_files = []
#     for upload_file in files:
#         saved_path = job_dir / upload_file.filename
#         with open(saved_path, 'wb') as f:
#             content = await upload_file.read()
#             f.write(content)
        
#         # Extract/collect valid code files
#         extracted = process_upload(saved_path, job_dir / "extracted")
#         all_files.extend(extracted)
    
#     print(f"📂 Found {len(all_files)} valid code files")
    
#     # Step 2: Group by language
#     fragments_by_lang = defaultdict(list)
#     skipped_files = [] # Track bad files

#     for idx, file_path in enumerate(all_files):
#         lang = LanguageDetector.detect(file_path.name)
#         if lang:
#             frags = FragmentExtractor.extract(file_path, idx, lang)
#             if frags:
#                 fragments_by_lang[lang].extend(frags)
#                 print(f"  📄 {file_path.name} → {len(frags)} fragments ({lang})")
#             else:
#                 # If extraction returned empty, it likely failed parsing or was empty
#                 print(f"  ⚠️ Skipping {file_path.name} (Parse Error or Empty)")
#                 skipped_files.append({
#                     "file": file_path.name,
#                     "reason": "Syntax Error or Empty File"
#                 })

#     # Step 3: Run detectors per language
#     config = {'min_lines': 2}  # Low threshold to catch small functions
    
#     detectors = [
#         Type1HashMethod(config),
#         Type1StringMethod(config),
#         Type1ASTMethod(config)  # Runs on ALL languages now (Token fallback)
#     ]
    
#     final_matches = []
#     language_summary = {}
    
#     for lang, fragments in fragments_by_lang.items():
#         print(f"\n🔍 Analyzing {lang.upper()} ({len(fragments)} fragments)...")
        
#         if len(fragments) < 2:
#             print(f"   ⚠️ Skipping {lang}: Need at least 2 fragments")
#             language_summary[lang] = 0
#             continue
        
#         best_count = 0
        
#         for detector in detectors:
#             try:
#                 result = detector.detect_clones(fragments)
#                 count = result['clones_found']
                
#                 print(f"   {detector.method_name}: {count} clones")
                
#                 if count > 0:
#                     # Tag matches with language and detector
#                     for match in result['matches']:
#                         match['language'] = lang
#                         match['detector'] = detector.method_name
                    
#                     final_matches.extend(result['matches'])
#                     best_count = max(best_count, count)
            
#             except Exception as e:
#                 print(f"   ❌ Error: {e}")
        
#         language_summary[lang] = best_count
    
#     # --- NEW: TRUE ACCURACY CALCULATION ---
#     # 1. Identify Total UNIQUE Clone Pairs
#     # We create a set of unique signatures: "FileA:Line1-FileB:Line2"
#     unique_pairs = set()
#     for match in final_matches:
#         # Sort file names to ensure "A vs B" is same as "B vs A"
#         f1, f2 = sorted([match['file1'], match['file2']])
#         pair_sig = f"{f1}:{match['line1']}-{f2}:{match['line2']}"
#         unique_pairs.add(pair_sig)
    
#     total_unique_count = len(unique_pairs)
    
#     # 2. Score methods based on how many UNIQUE pairs they found
#     accuracy_report = {}
#     best_method = "None"
#     highest_score = -1
    
#     if total_unique_count > 0:
#         for method_obj in detectors:
#             name = method_obj.method_name
#             # Count how many matches THIS method contributed
#             method_count = sum(1 for m in final_matches if m['detector'] == name)
            
#             # MATH FIX: Divide by UNIQUE count to show True Accuracy
#             # If method found 28 and unique is 28, result is 100%
#             # Cap at 100% just in case overlaps cause method_count > unique
#             accuracy = min(100, int((method_count / total_unique_count) * 100))
#             accuracy_report[name] = f"{accuracy}% accuracy"
            
#             # Track the winner
#             if method_count > highest_score:
#                 highest_score = method_count
#                 best_method = name
#     else:
#         accuracy_report = {"All Methods": "N/A"}

#     # Clean up temporary files
#     try:
#         shutil.rmtree(job_dir)
#     except:
#         pass
    
#     total_clones = sum(language_summary.values())
    
#     print(f"\n🏆 Best Method: {best_method}")
#     print(f"✅ Analysis Complete. Total Clones: {total_clones}\n{'='*60}")
    
#     return JSONResponse(content={
#         "status": "success",
#         "summary": {
#             "total_clones": total_clones,
#             "breakdown": language_summary,
#             "files_analyzed": len(all_files) - len(skipped_files),
#             "skipped_files": skipped_files,
#             "best_method": best_method,
#             "method_accuracy": accuracy_report
#         },
#         "matches": final_matches
#     })


# if __name__ == "__main__":
#     import uvicorn
#     print("🚀 Starting CodeSpectra Analysis Engine...")
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


"""
CodeSpectra Analysis Engine - Type 1 & Type 3 Hybrid Detection (Batch)
"""
import time
from pathlib import Path
from typing import List

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from detectors.type3.hybrid_detector import Type3HybridDetector

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("./data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Initialize Detector (you can tweak thresholds)
type3_detector = Type3HybridDetector(hybrid_threshold=0.45, ml_threshold=0.50)

@app.post("/api/analyze-type3-batch")
async def analyze_type3_batch(files: List[UploadFile] = File(...)):
    """
    1) Receives multiple .cpp files
    2) Trains batch frequency filter (boilerplate removal)
    3) Compares every file vs every other file
    4) Returns both Hybrid and ML results per pair
    """
    print(f"🚀 Starting Batch Analysis for {len(files)} files...")

    # 1) Save files
    job_id = f"batch_{int(time.time())}"
    job_dir = UPLOAD_DIR / job_id
    job_dir.mkdir(exist_ok=True)

    saved_paths: List[Path] = []
    for f in files:
        p = job_dir / f.filename
        content = await f.read()
        p.write_bytes(content)
        saved_paths.append(p)

    # 2) Train frequency filter on full batch for Winnowing
    type3_detector.prepare_batch(saved_paths)

    # 3) All-vs-All comparisons
    results = []
    for i in range(len(saved_paths)):
        for j in range(i + 1, len(saved_paths)):
            A = saved_paths[i]
            B = saved_paths[j]
            out = type3_detector.detect(A, B)  # returns {"hybrid": {...}, "ml": {... or None}}

            # Choose a filter threshold for inclusion (max of available scores)
            check_scores = [out["hybrid"]["score"]]
            if out["ml"] is not None:
                check_scores.append(out["ml"]["score"])
            include = max(check_scores) > 0.4

            if include:
                results.append({
                    "file_a": A.name,
                    "file_b": B.name,
                    # Hybrid (heuristics)
                    "hybrid_score": out["hybrid"]["score"],
                    "hybrid_is_clone": out["hybrid"]["is_clone"],
                    "winnowing_score": out["hybrid"]["details"]["winnowing_fingerprint_score"],
                    "ast_score": out["hybrid"]["details"]["ast_skeleton_score"],
                    "metric_score": out["hybrid"]["details"]["complexity_metric_score"],
                    # ML (RandomForest on named features)
                    "ml_score": (out["ml"]["score"] if out["ml"] is not None else None),
                    "ml_is_clone": (out["ml"]["is_clone"] if out["ml"] is not None else None),
                })

    # Sort by strongest signal (prefer ML if present; else hybrid)
    def sort_key(r):
        return max([s for s in [r.get("ml_score"), r.get("hybrid_score")] if s is not None])

    results.sort(key=sort_key, reverse=True)

    return {
        "status": "success",
        "total_files": len(saved_paths),
        "comparisons_made": (len(saved_paths) * (len(saved_paths) - 1)) // 2,
        "suspicious_pairs": len(results),
        "results": results,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)