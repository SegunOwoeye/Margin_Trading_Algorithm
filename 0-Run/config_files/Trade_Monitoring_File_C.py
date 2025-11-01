"""Legacy stub for creating trade monitoring wrapper scripts."""
from __future__ import annotations

import warnings
from typing import Sequence


def _warn_deprecated(name: str) -> None:
    warnings.warn(
        f"{name} is deprecated. The orchestrator now invokes the monitoring modules "
        "directly without generating pair specific files.",
        DeprecationWarning,
        stacklevel=2,
    )

# Main Function
class Create_Trade_Monitoring_Files:
    def __init__(
        self,
        trading_pair: Sequence[str],
        exchange: str,
        flag: int,
        chart_intervals: Sequence[str],
        Override: bool = False,
    ) -> None:
        self.trading_pair = tuple(trading_pair)
        self.exchange = exchange
        self.flag = flag
        self.chart_intervals = tuple(chart_intervals) if isinstance(chart_intervals, (list, tuple)) else (chart_intervals,)
        self.Override = Override

    
        self.exchange = exchange
        self.flag = flag
        self.Override = Override


    def create_asset_precision(self):  # type: ignore[no-untyped-def]
        _warn_deprecated("Create_Trade_Monitoring_Files.create_asset_precision")
        return []


    def create_HIR_files(self):  # type: ignore[no-untyped-def]
        _warn_deprecated("Create_Trade_Monitoring_Files.create_HIR_files")
        return []

