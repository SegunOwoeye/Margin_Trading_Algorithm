"""Legacy stub that previously generated pair specific data-gathering scripts."""
from __future__ import annotations

import warnings
from typing import List, Sequence

def _warn_deprecated(name: str) -> None:
    warnings.warn(
        f"{name} is deprecated. The orchestrator now launches the legacy modules "
        "directly via the runtime plan and no longer writes generated wrapper files.",
        DeprecationWarning,
        stacklevel=2,
    )

def create_data_gathering(
    trading_pair: Sequence[str],
    Time_Interval: Sequence[str],
    limit: int,
    levels: int,
) -> List[str]:
    """Return an empty list whilst warning that the helper is deprecated."""

    _warn_deprecated("create_data_gathering")
    return []
