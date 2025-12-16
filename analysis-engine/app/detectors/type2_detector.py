import hashlib
import os
import glob

# Pygments imports for tokenization
from pygments.lexers import guess_lexer_for_filename
from pygments.token import Token

# Placeholder token for normalization
NORMALIZED_TOKEN = "ID_P"

def normalize_code(file_path: str, code_string: str) -> str:
    """
    Tokenizes code and normalizes identifiers and literals for Type 2 detection.
    Returns a string of normalized tokens.
    """
    try:
        # Guess the language lexer (C, C++, etc.) based on the file extension
        lexer = guess_lexer_for_filename(file_path, code_string)
    except Exception:
        # Fallback if Pygments can't recognize the file type
        return ""

    normalized_tokens = []
    
    for token_type, value in lexer.get_tokens(code_string):
        
        # 1. Skip non-code elements (Type 1 pre-processing)
        if token_type in Token.Comment or token_type in Token.Text:
            continue
        
        # 2. CRITICAL: Normalize Identifiers and Literals (Type 2 logic)
        # Token.Name: Variables, Functions, Classes
        # Token.Literal: Strings, Numbers, Floats
        if token_type in Token.Name or token_type in Token.Literal:
            normalized_tokens.append(NORMALIZED_TOKEN)
        
        # 3. Keep all other tokens (keywords, operators, punctuation) as is
        else:
            normalized_tokens.append(value)

    # Return a space-separated string of normalized tokens ready for hashing
    return " ".join(normalized_tokens)

def get_code_hash(normalized_code: str) -> str:
    """Calculates the SHA256 hash of the normalized token string."""
    # Use hashlib for a fast, cryptographic hash
    return hashlib.sha256(normalized_code.encode('utf-8')).hexdigest()

def detect_type2_clones(directory_path: str, language_patterns: list) -> dict:
    """
    Scans a directory for Type 2 clones (renamed identifiers/literals).
    """
    clones = {}
    file_hashes = {}
    
    # 1. Gather all target files based on provided language patterns (e.g., ['*.c', '*.cpp'])
    target_files = []
    for pattern in language_patterns:
        target_files.extend(glob.glob(os.path.join(directory_path, pattern)))
        
    # 2. Process each file: Normalize, Hash, and Store
    for file_path in target_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Normalize and hash the entire file content
            normalized_code = normalize_code(file_path, code)
            code_hash = get_code_hash(normalized_code)
            
            # 3. Store the file path under its hash
            if code_hash not in file_hashes:
                file_hashes[code_hash] = []
            file_hashes[code_hash].append(file_path)
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            continue

    # 4. Identify clones: any hash with more than one file is a clone group
    for code_hash, paths in file_hashes.items():
        if len(paths) > 1:
            clones[code_hash] = paths
            
    return clones