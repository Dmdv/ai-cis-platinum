"""
Registry of metal sanitization strategies.

Adding a new metal does NOT require editing this file. Each strategy module
registers itself via the :func:`register_sanitizer` decorator at import time;
the strategies are eagerly imported below to trigger registration.

Open for extension, closed for modification (Open–Closed Principle).
"""

from __future__ import annotations

from typing import Callable

from .base import MetalSanitizer

_REGISTRY: dict[str, MetalSanitizer] = {}


def register_sanitizer(metal_symbol: str) -> Callable[[type], type]:
    """Decorator that registers a concrete strategy class for a metal symbol.

    Example:
        @register_sanitizer("Cu")
        class CopperSanitizer:
            metal_symbol: str = "Cu"
            ...
    """

    def _register(cls: type) -> type:
        instance = cls()
        if not isinstance(instance, MetalSanitizer):
            raise TypeError(
                f"{cls.__name__} does not satisfy the MetalSanitizer protocol"
            )
        _REGISTRY[metal_symbol] = instance
        return cls

    return _register


def get_strategy(metal_symbol: str) -> MetalSanitizer:
    if metal_symbol not in _REGISTRY:
        raise KeyError(
            f"No sanitization strategy registered for metal {metal_symbol!r}"
        )
    return _REGISTRY[metal_symbol]


def registered_metals() -> tuple[str, ...]:
    """Return the set of metals with a registered sanitization strategy."""
    return tuple(sorted(_REGISTRY))


# Eager-import strategies so their @register_sanitizer decorators run.
# New metals: drop a `cu.py` / `re.py` / etc. in this package and add one
# import line here.
from . import platinum  # noqa: E402,F401
from . import gold      # noqa: E402,F401
# Future: from . import copper, rhenium, ruthenium, palladium
