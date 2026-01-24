"""
AST -> ML Adapter with robust C++ name fallback so IDs match pairs.csv (filename.cpp:functionName).
"""
from dataclasses import dataclass, asdict
from core.ast_processor import ASTProcessor
from typing import List, Dict, Tuple, Set, Any, Optional
import pathlib
import json
import hashlib
import numpy as np
import re
import os

CHAR_RE = re.compile(r"\'(\\.|[^\\'])\'")
IDENT_RE = re.compile(r'\b[_A-Za-z]\w*\b')
NUM_RE = re.compile(r'\b\d+(\.\d+)?\b')
STR_RE = re.compile(r'(\".*?\"|\'.*?\')', re.DOTALL)

COMMON_KEYWORDS = {
    'if','else','elif','for','while','return','def','class','import','from',
    'try','except','finally','with','break','continue','switch','case','default',
    'public','private','protected','static','void','int','float','double','long',
    'char','boolean','true','false','new','this','super','const','let','var','function',
    'string','bool','short','unsigned','signed','size_t','auto','long long'
}

CPP_FUNC_DEF_RE = re.compile(
    r"""
    ^
    (?:template\s*<[^>]*>\s*)?
    [^\n{;]*?
    \b([_A-Za-z]\w*)
    \s*\([^;{}]*\)
    \s*\{
    """,
    re.MULTILINE | re.VERBOSE
)

@dataclass
class Unit:
    id: str
    file_path: str
    func_name: Optional[str]
    start_line: int
    end_line: int
    code: str
    ast: Any
    normalized_ast: Any = None
    subtree_hashes: Optional[Set[str]] = None
    ast_paths: Optional[List[str]] = None
    features: Optional[Dict[str, Any]] = None
    vector: Optional[np.ndarray] = None

class ASTMLAdapter:
    def __init__(self, cache_dir: str = "core_cache", ast_processor: Optional[ASTProcessor] = None):
        self.cache_dir = pathlib.Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ast = ast_processor or ASTProcessor()

    def _infer_func_name_from_header(self, code_text: str) -> Optional[str]:
        header = code_text.split('{', 1)[0]
        header_lines = header.splitlines()[:5]
        header_text = ' '.join(header_lines)
        candidates = re.findall(r'([_A-Za-z]\w*)\s*\(', header_text)
        for cand in reversed(candidates):
            if cand not in COMMON_KEYWORDS:
                return cand
        return candidates[-1] if candidates else None

    def _fallback_cpp_function_names(self, src: str) -> List[str]:
        names = []
        for m in CPP_FUNC_DEF_RE.finditer(src):
            cand = m.group(1)
            if cand and cand not in COMMON_KEYWORDS:
                names.append(cand)
        seen = set(); result = []
        for n in names:
            if n not in seen:
                seen.add(n); result.append(n)
        return result

    def build_units_from_file(self, file_path: str) -> List[Unit]:
        base = os.path.basename(file_path)
        try:
            parsed = self.ast.parse_file(file_path)
            root = parsed.get('root')
            src = parsed.get('source', "")
            src_bytes = parsed.get('source_bytes', None)
            lang = parsed.get('lang_key', None)
        except Exception:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    src = f.read()
            except Exception:
                src = ""
            units: List[Unit] = []
            for name in self._fallback_cpp_function_names(src):
                uid = f"{base}:{name}"
                units.append(Unit(
                    id=uid, file_path=file_path, func_name=name,
                    start_line=1, end_line=src.count("\n")+1, code=src, ast=None
                ))
            if not units:
                uid = self.uid_for(file_path, 1, src.count("\n")+1)
                units.append(Unit(id=uid, file_path=file_path, func_name=None,
                                  start_line=1, end_line=src.count("\n")+1, code=src, ast=None))
            return units

        funcs = []
        try:
            funcs = self.ast.extract_functions_from_tree(root, src_bytes, lang)
        except Exception:
            funcs = []

        units: List[Unit] = []
        if funcs:
            lines = src.splitlines()
            for f in funcs:
                start = f.get('start', 1)
                end = f.get('end', max(1, len(lines)))
                start_idx = max(0, start - 1)
                end_idx = min(len(lines), end)
                code_text = "\n".join(lines[start_idx:end_idx])

                func_name = f.get('name') or self._infer_func_name_from_header(code_text)
                if not func_name:
                    local_names = self._fallback_cpp_function_names(code_text)
                    func_name = local_names[0] if local_names else None

                uid = f"{base}:{func_name}" if func_name else self.uid_for(file_path, start, end)
                units.append(Unit(
                    id=uid, file_path=file_path, func_name=func_name,
                    start_line=start, end_line=end, code=code_text, ast=f.get('node')
                ))

        if not units:
            for name in self._fallback_cpp_function_names(src):
                uid = f"{base}:{name}"
                units.append(Unit(
                    id=uid, file_path=file_path, func_name=name,
                    start_line=1, end_line=src.count("\n")+1, code=src, ast=None
                ))

        if not units:
            uid = self.uid_for(file_path, 1, src.count("\n")+1)
            units.append(Unit(
                id=uid, file_path=file_path, func_name=None,
                start_line=1, end_line=src.count("\n")+1, code=src, ast=root
            ))
        return units

    def save_unit_repr(self, unit: Unit) -> str:
        uid = unit.id
        out_json = self.cache_dir / f"{uid}.json"
        data = asdict(unit)
        data.pop("ast", None)
        data.pop("normalized_ast", None)
        if isinstance(unit.subtree_hashes, set):
            data['subtree_hashes'] = list(unit.subtree_hashes)
        vec = unit.vector
        data["vector_path"] = None
        with out_json.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        if vec is not None:
            np.save(self.cache_dir / f"{uid}.npy", vec)
            data["vector_path"] = str(self.cache_dir / f"{uid}.npy")
            with out_json.open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        return str(out_json)

    def load_unit_repr(self, unit_id: str) -> Unit:
        json_path = self.cache_dir / f"{unit_id}.json"
        if not json_path.exists():
            raise FileNotFoundError(f"No cached unit for id {unit_id}")
        data = json.loads(json_path.read_text(encoding="utf-8"))
        vec_path = data.get("vector_path")
        vec = None
        if vec_path:
            try:
                vec = np.load(vec_path)
            except Exception:
                vec = None
        unit = Unit(
            id=data.get("id"),
            file_path=data.get("file_path"),
            func_name=data.get("func_name"),
            start_line=data.get("start_line", 1),
            end_line=data.get("end_line", 1),
            code=data.get("code", ""),
            ast=None,
            normalized_ast=None,
            subtree_hashes=set(data.get("subtree_hashes", [])) if data.get("subtree_hashes") else None,
            ast_paths=data.get("ast_paths"),
            features=data.get("features"),
            vector=vec
        )
        return unit

    def normalize_unit(self, unit: Unit, id_map_seed: Optional[int] = None) -> Unit:
        code = unit.code or ""
        code = STR_RE.sub(" STR ", code)
        code = CHAR_RE.sub(" CHAR ", code)
        code = NUM_RE.sub(" NUM ", code)
        id_map: Dict[str, str] = {}
        next_id = 1
        def replace_ident(m):
            nonlocal next_id
            token = m.group(0)
            if token in COMMON_KEYWORDS:
                return token
            if token not in id_map:
                id_map[token] = f"ID{next_id}"
                next_id += 1
            return id_map[token]
        code = IDENT_RE.sub(replace_ident, code)
        code = re.sub(r'\s+', ' ', code).strip()
        unit.normalized_ast = code
        unit.features = unit.features or {}
        unit.features['id_map'] = id_map
        return unit

    def compute_subtree_hashes(self, unit: Unit, max_height: Optional[int] = None) -> Set[str]:
        text = unit.normalized_ast or unit.code or ""
        tokens = text.split()
        k = 5
        hashes: Set[str] = set()
        if len(tokens) == 0:
            unit.subtree_hashes = hashes
            return hashes
        if len(tokens) < k:
            combined = " ".join(tokens)
            h = hashlib.md5(combined.encode("utf-8")).hexdigest()
            hashes.add(h)
        else:
            for i in range(len(tokens) - k + 1):
                gram = " ".join(tokens[i:i+k])
                h = hashlib.md5(gram.encode("utf-8")).hexdigest()
                hashes.add(h)
        unit.subtree_hashes = hashes
        return hashes

    def extract_ast_paths(self, unit: Unit, max_path_len: int = 6) -> List[str]:
        if not unit.normalized_ast:
            unit = self.normalize_unit(unit)
        text = unit.normalized_ast or unit.code or ""
        tokens = text.split()
        paths: List[str] = []
        if not tokens:
            unit.ast_paths = []
            return []
        L = len(tokens)
        cap = 5000
        for i in range(L):
            max_j = min(L, i + max_path_len + 1)
            for j in range(i + 1, max_j):
                paths.append(f"{tokens[i]}|{tokens[j]}")
                if len(paths) >= cap:
                    break
            if len(paths) >= cap:
                break
        unit.ast_paths = paths
        return paths

    def compute_ast_counts(self, unit: Unit) -> Dict[str, int]:
        if not unit.normalized_ast:
            unit = self.normalize_unit(unit)
        text = unit.normalized_ast or ""
        features: Dict[str, int] = {}
        tokens = text.split()
        features['token_count'] = len(tokens)
        features['if_count'] = text.count(' if ')
        features['for_count'] = text.count(' for ')
        features['while_count'] = text.count(' while ')
        features['return_count'] = text.count(' return ')
        features['call_approx'] = unit.code.count('(')
        unit.features = unit.features or {}
        unit.features.update(features)
        return features

    def vectorize_units(self, units: List[Unit], method: str = "tfidf") -> Tuple[np.ndarray, List[str]]:
        ids = [u.id for u in units]
        if method == "tfidf":
            docs = []
            for u in units:
                if not u.ast_paths:
                    self.extract_ast_paths(u)
                docs.append(" ".join(u.ast_paths or []))
            try:
                from sklearn.feature_extraction.text import TfidfVectorizer
            except Exception:
                method = "hashset"
        if method == "tfidf":
            from sklearn.feature_extraction.text import TfidfVectorizer
            vec = TfidfVectorizer(max_features=4096)
            X = vec.fit_transform(docs).toarray().astype(np.float32)
            for i, u in enumerate(units):
                u.vector = X[i]
            return X, ids
        rows = []
        for u in units:
            hcount = len(u.subtree_hashes) if u.subtree_hashes else 0
            tcount = len((u.normalized_ast or "").split())
            rows.append([float(hcount), float(tcount)])
        X = np.array(rows, dtype=np.float32)
        for i, u in enumerate(units):
            u.vector = X[i]
        return X, ids

    def make_pair_features(self, ua: Unit, ub: Unit) -> Dict[str, float]:
        """
        Build named, stable pair-level features for serving.
        """
        # Ensure required fields are present
        if ua.normalized_ast is None: self.normalize_unit(ua)
        if ub.normalized_ast is None: self.normalize_unit(ub)
        if ua.subtree_hashes is None: self.compute_subtree_hashes(ua)
        if ub.subtree_hashes is None: self.compute_subtree_hashes(ub)
        if ua.ast_paths is None: self.extract_ast_paths(ua)
        if ub.ast_paths is None: self.extract_ast_paths(ub)
        if ua.features is None: self.compute_ast_counts(ua)
        if ub.features is None: self.compute_ast_counts(ub)

        # Jaccard on subtree hashes
        A = ua.subtree_hashes or set()
        B = ub.subtree_hashes or set()
        inter = len(A & B)
        union = max(1, len(A | B))
        jaccard = inter / union

        # Cosine on path bags (fit on the two docs to get a stable similarity)
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            docs = [" ".join(ua.ast_paths or []), " ".join(ub.ast_paths or [])]
            vec = TfidfVectorizer(max_features=4096)
            X = vec.fit_transform(docs)
            cos = float(cosine_similarity(X[0], X[1])[0, 0])
        except Exception:
            cos = 0.0

        ta = (ua.features or {}).get("token_count", 0)
        tb = (ub.features or {}).get("token_count", 0)
        avg_tok = 0.5 * (ta + tb)
        abs_diff = abs(ta - tb)

        return {
            "jaccard_subtrees": float(jaccard),
            "cosine_paths": float(cos),
            "abs_token_count_diff": float(abs_diff),
            "avg_token_count": float(avg_tok),
        }

    def uid_for(self, file_path: str, start_line: int, end_line: int) -> str:
        key = f"{os.path.abspath(file_path)}:{start_line}:{end_line}"
        import hashlib
        return hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]