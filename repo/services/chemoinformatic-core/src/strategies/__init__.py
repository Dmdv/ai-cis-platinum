"""Registry of metal sanitization strategies."""

from .base import MetalSanitizer
from .platinum import PlatinumSanitizer
from .gold import GoldSanitizer


REGISTRY: dict[str, MetalSanitizer] = {
    "Pt": PlatinumSanitizer(),
    "Au": GoldSanitizer(),
    # Cu, Re, Ru, Pd strategies added in Phases 1–2.
}


def get_strategy(metal_symbol: str) -> MetalSanitizer:
    if metal_symbol not in REGISTRY:
        raise KeyError(f"No sanitization strategy registered for metal {metal_symbol!r}")
    return REGISTRY[metal_symbol]
