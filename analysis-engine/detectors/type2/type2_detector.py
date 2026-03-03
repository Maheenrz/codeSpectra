"""
analysis-engine/detectors/type2/type2_detector.py

Type-2 Clone Detector — renamed variable detection.
Normalises all user identifiers → 'ID', literals → 'NUM'/'STR',
then compares the normalised token stream with SequenceMatcher.
"""
import re
import difflib
from pathlib import Path
from typing import Any, Dict, List


class Type2Detector:

    KEYWORDS = {
        # C/C++
        'int','float','double','char','bool','void','string','auto','long','short',
        'unsigned','signed','const','static','extern','inline','virtual','override',
        'if','else','for','while','do','switch','case','break','continue','return',
        'class','struct','union','enum','public','private','protected','friend',
        'new','delete','nullptr','null','true','false','this','operator','template',
        'cout','cin','endl','printf','scanf','std','vector','map','set','pair',
        # Java
        'import','package','extends','implements','interface','abstract','final',
        'throws','throw','try','catch','finally','instanceof','super',
        # Python
        'def','lambda','with','in','is','not','and','or','pass','yield',
        'print','len','range','list','dict','tuple','set','str','type',
        # JS/TS
        'function','var','let','const','typeof','instanceof','async','await',
        'export','require','module','console','log','undefined',
    }

    def _tokenize(self, code: str) -> List[str]:
        # Strip comments
        code = re.sub(r'//[^\n]*', '', code)
        code = re.sub(r'#[^\n]*',  '', code)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
        code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)
        # Replace string literals before tokenising
        code = re.sub(r'"[^"]*"', ' STR ', code)
        code = re.sub(r"'[^']*'", ' STR ', code)
        # Raw token split
        raw = re.findall(
            r'[a-zA-Z_]\w*|'        # identifiers / keywords
            r'\d+\.?\d*|'           # numbers
            r'[+\-*/=<>!&|^%~]+|'  # operators
            r'[(){}\[\];,.]',        # punctuation
            code
        )
        tokens = []
        for tok in raw:
            low = tok.lower()
            if low in self.KEYWORDS:
                tokens.append(low)
            elif re.match(r'^\d', tok):
                tokens.append('NUM')
            elif re.match(r'^[a-zA-Z_]', tok):
                tokens.append('ID')
            else:
                tokens.append(tok)
        return tokens

    def detect(self, file_a: str, file_b: str) -> Dict[str, Any]:
        try:
            code_a = Path(file_a).read_text(encoding='utf-8', errors='ignore')
            code_b = Path(file_b).read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            return {"type2_score": 0.0, "is_clone": False, "confidence": "ERROR", "error": str(e)}

        tokens_a = self._tokenize(code_a)
        tokens_b = self._tokenize(code_b)

        if not tokens_a or not tokens_b:
            return {"type2_score": 0.0, "is_clone": False, "confidence": "EMPTY"}

        ratio = round(difflib.SequenceMatcher(None, tokens_a, tokens_b).ratio(), 4)

        is_clone   = ratio >= 0.70
        confidence = (
            "HIGH"     if ratio >= 0.85 else
            "MEDIUM"   if ratio >= 0.70 else
            "LOW"      if ratio >= 0.50 else
            "UNLIKELY"
        )

        return {
            "type2_score":   ratio,
            "is_clone":      is_clone,
            "confidence":    confidence,
            "token_count_a": len(tokens_a),
            "token_count_b": len(tokens_b),
        }