from dataclasses import dataclass
from typing import Dict

@dataclass(frozen=True)
class SymbolMap:
    canonical_to_provider: Dict[str, str]

    def to_provider(self, canonical: str) -> str:
        if canonical not in self.canonical_to_provider:
            raise KeyError(f"Missing provider mapping for symbol: {canonical}")
        return self.canonical_to_provider[canonical]

#    Expects cfg['symbol_mapping']['stooq'] dict: canonical -> provider symbol.
#    Example: QQQM -> qqqm.us
def build_stooq_map_from_config(cfg: dict) -> SymbolMap:
    mapping = (cfg.get("symbol_mapping") or {}).get("stooq") or {}
    return SymbolMap(canonical_to_provider=mapping)

def build_yahoo_map_from_config(cfg: dict) -> SymbolMap:
    mapping = (cfg.get("symbol_mapping") or {}).get("yahoo") or {}
    return SymbolMap(canonical_to_provider=mapping)
