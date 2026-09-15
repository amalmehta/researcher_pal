"""Load an exercise's impl.py by folder name, e.g. load("01_softmax").

Paths are resolved next to this file, so the same code works in exercises/ and in a
copy with the reference solutions swapped in.
"""
import importlib.util
from pathlib import Path

_HERE = Path(__file__).parent
_cache = {}


def load(folder):
    if folder not in _cache:
        path = _HERE / folder / "impl.py"
        spec = importlib.util.spec_from_file_location("ex_" + folder, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _cache[folder] = module
    return _cache[folder]
