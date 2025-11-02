"""Legacy stub for generating per-pair indicator wrapper scripts."""
from __future__ import annotations

import warnings
from typing import List, Sequence

def _warn_deprecated(name: str) -> None:
    warnings.warn(
        f"{name} is deprecated. Indicator scripts are no longer generated on disk; "
        "the runtime plan now targets the legacy modules directly.",
        DeprecationWarning,
        stacklevel=2,
    )

def create_indicators(
    trading_pair: Sequence[str],
    Exchange: str,
    Time_Interval: Sequence[str],
    SA_interval: int,
    TA_interval: int,
) -> List[str]:
    """Return an empty list whilst warning that the helper is deprecated."""

    _warn_deprecated("create_indicators")
    return []





