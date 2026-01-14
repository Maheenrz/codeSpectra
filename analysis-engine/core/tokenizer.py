# tokenizer.py
from pygments import lex
from pygments.lexers import get_lexer_for_filename, guess_lexer
from pygments.token import Token

class CodeTokenizer:
    def tokenize_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
            
            # ADAPTIVE LOGIC: Only hide IDs if file is large enough to have structure
            hide_identifiers = len(code.splitlines()) > 15 

            lexer = get_lexer_for_filename(file_path)
            raw_tokens = lex(code, lexer)
            normalized_tokens = []

            for token_type, value in raw_tokens:
                if token_type in Token.Comment or token_type in Token.Text:
                    continue
                
                if token_type in Token.Name and hide_identifiers:
                    normalized_tokens.append("ID")
                elif token_type in Token.Literal.String:
                    normalized_tokens.append("STR")
                elif token_type in Token.Literal.Number:
                    normalized_tokens.append("NUM")
                else:
                    normalized_tokens.append(value.strip())
            return normalized_tokens
        except: return []