"""Planning utilities for orchestrating the legacy runtime."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import chain
from pathlib import Path
from typing import List, Mapping, Optional, Sequence

from .command import CommandSpec

ROOT = Path(__file__).resolve().parents[1]


def _load_config() -> Mapping[str, object]:
    import json

    config_path = ROOT / "0-Settings" / "config.json"
    with config_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _serialise_value(value: object) -> str:
    if isinstance(value, Path):
        return repr(str(value))
    return repr(value)


@dataclass
class StrategyPlan:
    """Build command specifications for the configured trading stack."""

    config: Mapping[str, object]
    runner_module: str = "orchestration.runners.legacy"
    repository_root: Path = ROOT

    @classmethod
    def from_config(cls, config: Optional[Mapping[str, object]] = None) -> "StrategyPlan":
        return cls(config=config or _load_config())

    # ------------------------------------------------------------------
    # Properties exposing configuration shortcuts
    # ------------------------------------------------------------------
    @property
    def application_settings(self) -> Mapping[str, object]:
        return self.config["application_settings"]  # type: ignore[index]

    @property
    def data_gathering_settings(self) -> Mapping[str, object]:
        return self.application_settings["data_gathering"]  # type: ignore[index]

    @property
    def data_processing_settings(self) -> Mapping[str, object]:
        return self.application_settings["data_processing"]  # type: ignore[index]

    @property
    def trading_pairs(self) -> Sequence[str]:
        return tuple(self.application_settings["pair_list"])  # type: ignore[index]

    @property
    def time_intervals(self) -> Sequence[str]:
        return tuple(self.data_gathering_settings["time_intervals"])  # type: ignore[index]

    @property
    def exchange(self) -> str:
        program = self.config.get("program", {})  # type: ignore[arg-type]
        return program.get("exchange", "Binance")  # type: ignore[return-value]

    @property
    def environment_flag(self) -> int:
        trading_env = self.application_settings["trading_environment"]  # type: ignore[index]
        return int(trading_env.get("flag", 0))  # type: ignore[arg-type]

    @property
    def strategies(self) -> Sequence[str]:
        return tuple(self.application_settings.get("strategies", []))  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _module_root(self, *parts: str) -> Path:
        return self.repository_root.joinpath(*parts)

    def _base_command(self, module: str, module_roots: Sequence[Path]) -> List[str]:
        command = ["python", "-m", self.runner_module, "--module", module]
        for root in module_roots:
            command.extend(["--module-root", str(root)])
        if self.exchange:
            command.extend(["--exchange", self.exchange])
        command.extend(["--environment", str(self.environment_flag)])
        return command

    def _create_command(
        self,
        *,
        name: str,
        module: str,
        module_roots: Sequence[Path],
        pair: Optional[str] = None,
        interval: Optional[str] = None,
        limit: Optional[int] = None,
        levels: Optional[int] = None,
        params: Optional[Mapping[str, object]] = None,
        tags: Optional[Mapping[str, str]] = None,
    ) -> CommandSpec:
        command = self._base_command(module, module_roots)
        if pair is not None:
            command.extend(["--pair", pair])
        if interval is not None:
            command.extend(["--interval", interval])
        if limit is not None:
            command.extend(["--limit", str(limit)])
        if levels is not None:
            command.extend(["--levels", str(levels)])
        if params:
            for key, value in params.items():
                command.extend(["--param", f"{key}={_serialise_value(value)}"])
        return CommandSpec(command=command, name=name, tags=tags or {})

    # ------------------------------------------------------------------
    # Command builders for each pipeline stage
    # ------------------------------------------------------------------
    def data_gathering_commands(self) -> List[CommandSpec]:
        commands: List[CommandSpec] = []
        module_root = [self._module_root("1-DataGathering", "Programs")]
        historical_limit = int(self.data_gathering_settings.get("historical_data_limit", 1000))
        orderbook_levels = int(self.data_gathering_settings.get("orderbook_levels", 5))

        for pair in self.trading_pairs:
            for interval in self.time_intervals:
                commands.append(
                    self._create_command(
                        name=f"historical:{pair}:{interval}",
                        module="Data_Gathering_Binance_Historical_LEGACY",
                        module_roots=module_root,
                        pair=pair,
                        interval=interval,
                        limit=historical_limit,
                        tags={"phase": "data_gathering", "kind": "historical"},
                    )
                )
                commands.append(
                    self._create_command(
                        name=f"live:{pair}:{interval}",
                        module="Data_Gathering_Binance_Live_LEGACY",
                        module_roots=module_root,
                        pair=pair,
                        interval=interval,
                        tags={"phase": "data_gathering", "kind": "live"},
                    )
                )
            commands.append(
                self._create_command(
                    name=f"orderbook:{pair}",
                    module="Data_Gathering_Binance_Orderbook_LEGACY",
                    module_roots=module_root,
                    pair=pair,
                    levels=orderbook_levels,
                    tags={"phase": "data_gathering", "kind": "orderbook"},
                )
            )
        return commands

    def technical_analysis_commands(self) -> List[CommandSpec]:
        commands: List[CommandSpec] = []
        module_root = [self._module_root("2-DataProcessing", "Programs")]

        defaults = {
            "Average_True_Range_Legacy": 14,
            "Mean_Reversion_Legacy": 100,
            "GARCH_Model_Legacy": 1000,
        }

        for pair in self.trading_pairs:
            for interval in self.time_intervals:
                commands.append(
                    self._create_command(
                        name=f"atr:{pair}:{interval}",
                        module="Average_True_Range_Legacy",
                        module_roots=module_root,
                        pair=pair,
                        interval=interval,
                        params={"indicator_interval": defaults["Average_True_Range_Legacy"]},
                        tags={"phase": "technical", "indicator": "atr"},
                    )
                )
                commands.append(
                    self._create_command(
                        name=f"garch:{pair}:{interval}",
                        module="GARCH_Model_Legacy",
                        module_roots=module_root,
                        pair=pair,
                        interval=interval,
                        params={"indicator_interval": defaults["GARCH_Model_Legacy"]},
                        tags={"phase": "technical", "indicator": "garch"},
                    )
                )
                commands.append(
                    self._create_command(
                        name=f"mean-reversion:{pair}:{interval}",
                        module="Mean_Reversion_Legacy",
                        module_roots=module_root,
                        pair=pair,
                        interval=interval,
                        params={"indicator_interval": defaults["Mean_Reversion_Legacy"]},
                        tags={"phase": "technical", "indicator": "mean_reversion"},
                    )
                )

        sma_intervals: Sequence[int] = tuple(
            chain(
                self.data_processing_settings.get("sma_long_intervals", []),
                self.data_processing_settings.get("sma_short_intervals", []),
            )
        )  # type: ignore[arg-type]
        ema_intervals: Sequence[int] = tuple(
            chain(
                self.data_processing_settings.get("ema_long_intervals", []),
                self.data_processing_settings.get("ema_short_intervals", []),
            )
        )  # type: ignore[arg-type]
        wf_intervals: Sequence[int] = tuple(
            self.data_processing_settings.get("wf_intervals", [])
        )  # type: ignore[arg-type]
        rsi_intervals: Sequence[int] = tuple(
            self.data_processing_settings.get("rsi_intervals", [])
        )  # type: ignore[arg-type]
        wfc_intervals: Sequence[int] = tuple(
            self.data_processing_settings.get("wfc_intervals", [])
        )  # type: ignore[arg-type]

        for pair in self.trading_pairs:
            for interval in self.time_intervals:
                for indicator in sma_intervals:
                    commands.append(
                        self._create_command(
                            name=f"sma:{pair}:{interval}:{indicator}",
                            module="Simple_Moving_Average_Legacy",
                            module_roots=module_root,
                            pair=pair,
                            interval=interval,
                            params={"indicator_interval": indicator},
                            tags={"phase": "technical", "indicator": "sma"},
                        )
                    )
                for indicator in ema_intervals:
                    commands.append(
                        self._create_command(
                            name=f"ema:{pair}:{interval}:{indicator}",
                            module="Exponential_Moving_Average_Legacy",
                            module_roots=module_root,
                            pair=pair,
                            interval=interval,
                            params={"indicator_interval": indicator},
                            tags={"phase": "technical", "indicator": "ema"},
                        )
                    )
                for indicator in wf_intervals:
                    commands.append(
                        self._create_command(
                            name=f"wf:{pair}:{interval}:{indicator}",
                            module="Williams_Fractals_Legacy",
                            module_roots=module_root,
                            pair=pair,
                            interval=interval,
                            params={"indicator_interval": indicator},
                            tags={"phase": "technical", "indicator": "wf"},
                        )
                    )
                for indicator in rsi_intervals:
                    commands.append(
                        self._create_command(
                            name=f"rsi:{pair}:{interval}:{indicator}",
                            module="Relative_Strength_Indicator_Legacy",
                            module_roots=module_root,
                            pair=pair,
                            interval=interval,
                            params={"indicator_interval": indicator},
                            tags={"phase": "technical", "indicator": "rsi"},
                        )
                    )
                for indicator in wfc_intervals:
                    commands.append(
                        self._create_command(
                            name=f"wfc:{pair}:{interval}:{indicator}",
                            module="Williams_Fractal_Cap_Legacy",
                            module_roots=module_root,
                            pair=pair,
                            interval=interval,
                            params={"indicator_interval": indicator},
                            tags={"phase": "technical", "indicator": "wfc"},
                        )
                    )

        return commands

    def statistical_analysis_commands(self) -> List[CommandSpec]:
        commands: List[CommandSpec] = []
        module_root = [self._module_root("2-DataProcessing", "Programs")]
        if not self.trading_pairs:
            return commands
        base_pair = self.trading_pairs[0]
        other_pairs = self.trading_pairs[1:]
        for pair in other_pairs:
            trading_pairs = [base_pair, pair]
            for interval in self.time_intervals:
                commands.append(
                    self._create_command(
                        name=f"cointegration:{base_pair}:{pair}:{interval}",
                        module="Cointegration_Legacy",
                        module_roots=module_root,
                        pair=base_pair,
                        interval=interval,
                        params={"trading_pairs": trading_pairs},
                        tags={"phase": "statistical", "indicator": "cointegration"},
                    )
                )
        return commands

    def strategy_commands(self) -> List[CommandSpec]:
        commands: List[CommandSpec] = []
        module_root = [self._module_root("4-Strategies", "Programs")]
        active_strategies = set(self.strategies)

        if "Strategy2_Orders" in active_strategies:
            ema_long: Sequence[int] = tuple(
                self.data_processing_settings.get("ema_long_intervals", [])
            )  # type: ignore[arg-type]
            ema_short: Sequence[int] = tuple(
                self.data_processing_settings.get("ema_short_intervals", [])
            )  # type: ignore[arg-type]
            rsi_intervals: Sequence[int] = tuple(
                self.data_processing_settings.get("rsi_intervals", [])
            )  # type: ignore[arg-type]
            if len(ema_long) < 3 or len(ema_short) < 3 or not rsi_intervals:
                raise ValueError("Strategy 2 requires EMA and RSI configuration values")
            strategy_defaults = {
                "leverage": 5,
                "L_TP": 0.9,
                "S_TP": 0.7,
                "L_SL": 0.7,
                "S_SL": 0.6,
                "tradeable_fund_Percentage": 50,
            }
            for pair in self.trading_pairs:
                for interval in self.time_intervals:
                    params = {
                        "emaL1_interval": ema_long[0],
                        "emaL2_interval": ema_long[1],
                        "emaL3_interval": ema_long[2],
                        "emaS1_interval": ema_short[0],
                        "emaS2_interval": ema_short[1],
                        "emaS3_interval": ema_short[2],
                        "rsi_interval": rsi_intervals[0],
                    }
                    params.update(strategy_defaults)
                    commands.append(
                        self._create_command(
                            name=f"strategy2:{pair}:{interval}",
                            module="Strategy_2_Legacy",
                            module_roots=module_root,
                            pair=pair,
                            interval=interval,
                            params=params,
                            tags={"phase": "strategy", "strategy": "2"},
                        )
                    )

        # Additional strategies (e.g., Strategy 7) can be added in future iterations.
        return commands

    def trade_monitoring_commands(self) -> List[CommandSpec]:
        commands: List[CommandSpec] = []
        module_root = [self._module_root("5-Trade_Monitoring", "Programs")]

        for pair in self.trading_pairs:
            commands.append(
                self._create_command(
                    name=f"asset_precision:{pair}",
                    module="asset_precision_Legacy",
                    module_roots=module_root,
                    pair=pair,
                    tags={"phase": "monitoring", "type": "precision"},
                )
            )
            commands.append(
                self._create_command(
                    name=f"hir:{pair}",
                    module="Hourly_Interest_Rate_Legacy",
                    module_roots=module_root,
                    pair=pair,
                    tags={"phase": "monitoring", "type": "interest"},
                )
            )

        if "Strategy2_Orders" in set(self.strategies):
            for pair in self.trading_pairs:
                for interval in self.time_intervals:
                    commands.append(
                        self._create_command(
                            name=f"orderbook-monitoring:{pair}:{interval}",
                            module="Orderbook_Monitoring_Legacy",
                            module_roots=module_root,
                            pair=pair,
                            interval=interval,
                            params={"db_name": "Strategy2_Orders"},
                            tags={"phase": "monitoring", "type": "orderbook", "strategy": "2"},
                        )
                    )

        return commands

    def risk_management_commands(self) -> List[CommandSpec]:
        commands: List[CommandSpec] = []
        module_root = [self._module_root("8-Risk_Managment", "Programs")]

        if "Strategy2_Orders" not in set(self.strategies):
            return commands

        for pair in self.trading_pairs:
            for interval in self.time_intervals:
                commands.append(
                    self._create_command(
                        name=f"trailing-stop:{pair}:{interval}",
                        module="Trailing_Stop_Loss",
                        module_roots=module_root,
                        pair=pair,
                        interval=interval,
                        params={"db_name": "Strategy2_Orders"},
                        tags={"phase": "risk", "strategy": "2"},
                    )
                )
        return commands

    def command_groups(self) -> Mapping[str, Sequence[CommandSpec]]:
        return {
            "data_gathering": self.data_gathering_commands(),
            "technical_analysis": self.technical_analysis_commands(),
            "statistical_analysis": self.statistical_analysis_commands(),
            "strategy": self.strategy_commands(),
            "trade_monitoring": self.trade_monitoring_commands(),
            "risk_management": self.risk_management_commands(),
        }


class RuntimePlan(StrategyPlan):
    """Expanded plan used by the runtime orchestrator."""

    def commands(self) -> List[CommandSpec]:
        groups = self.command_groups()
        ordered_keys = [
            "data_gathering",
            "technical_analysis",
            "statistical_analysis",
            "strategy",
            "trade_monitoring",
            "risk_management",
        ]
        commands: List[CommandSpec] = []
        for key in ordered_keys:
            commands.extend(groups.get(key, ()))
        return commands
