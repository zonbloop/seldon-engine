from pathlib import Path
from typing import List
import yaml

def load_universe_config(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def extract_canonical_symbols(cfg: dict) -> List[str]:
    regions = cfg.get("regions", {})
    symbols: list[str] = []

    def walk(node):
        if isinstance(node, list):
            symbols.extend(node)
        elif isinstance(node, dict):
            for v in node.values():
                walk(v)

    walk(regions)
    # de-dup while preserving order
    seen = set()
    out = []
    for s in symbols:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out
