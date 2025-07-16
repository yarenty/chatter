from typing import Callable

# Simple ratio using difflib
from difflib import SequenceMatcher

def simple_ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

# Explicit difflib similarity (same as simple_ratio, but registered separately)
try:
    from difflib import SequenceMatcher as _SequenceMatcher
    def difflib_similarity(a: str, b: str) -> float:
        return _SequenceMatcher(None, a, b).ratio()
    _has_difflib = True
except ImportError:
    def difflib_similarity(a: str, b: str) -> float:
        return float(a == b)
    _has_difflib = False

# Levenshtein distance (requires python-Levenshtein)
try:
    import Levenshtein
    def levenshtein_ratio(a: str, b: str) -> float:
        return Levenshtein.ratio(a, b)
    _has_lev = True
except ImportError:
    def levenshtein_ratio(a: str, b: str) -> float:
        raise ImportError("Levenshtein module not installed")
    _has_lev = False

# Jaro-Winkler (requires jellyfish)
try:
    import jellyfish
    def jaro_winkler(a: str, b: str) -> float:
        return jellyfish.jaro_winkler_similarity(a, b)
    _has_jaro = True
except ImportError:
    def jaro_winkler(a: str, b: str) -> float:
        raise ImportError("jellyfish module not installed")
    _has_jaro = False

# Hamming distance (only for equal length strings)
def hamming_ratio(a: str, b: str) -> float:
    if len(a) != len(b):
        return 0.0
    return sum(x == y for x, y in zip(a, b)) / len(a) if a else 1.0

SIMILARITY_ALGORITHMS = {
    'simple': simple_ratio,
    'difflib': difflib_similarity if _has_difflib else None,
    'levenshtein': levenshtein_ratio if _has_lev else None,
    'jaro': jaro_winkler if _has_jaro else None,
    'hamming': hamming_ratio,
}

AVAILABLE_ALGORITHMS = [k for k, v in SIMILARITY_ALGORITHMS.items() if v is not None]

def get_similarity_func(name: str) -> Callable[[str, str], float]:
    if name not in SIMILARITY_ALGORITHMS or SIMILARITY_ALGORITHMS[name] is None:
        raise ValueError(f"Similarity algorithm '{name}' is not available. Available: {AVAILABLE_ALGORITHMS}")
    return SIMILARITY_ALGORITHMS[name] 