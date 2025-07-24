from __future__ import annotations
import sys
from pathlib import Path

def ensure_project_root():
    here = Path(__file__).resolve()
    for p in [here, *here.parents]:
        if (p / "pyproject.toml").exists():
            root = p
            break
    else:
        root = here.parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

ensure_project_root()
