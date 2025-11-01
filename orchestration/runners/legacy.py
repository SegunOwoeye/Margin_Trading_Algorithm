"""Command-line runner for invoking legacy modules with standardised arguments.

This runner provides a thin wrapper around the long-lived "LEGACY" modules that
power data gathering, data processing, strategy execution and trade monitoring.
The legacy scripts historically relied on generated pair specific wrapper files;
this runner removes that requirement by allowing the orchestrator to target the
original modules directly via CLI arguments or environment variables.
"""
from __future__ import annotations

import argparse
import ast
import inspect
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Mapping, MutableMapping, Optional

# Map logical argument categories to potential parameter names used by the
# legacy modules. This allows us to reuse a single CLI contract for multiple
# modules that expose slightly different run signatures.
ARGUMENT_ALIASES: Mapping[str, tuple[str, ...]] = {
    "pair": ("trading_pair", "exchange_pair", "pair", "base_pair"),
    "interval": ("interval", "chart_interval"),
    "limit": ("limit",),
    "exchange": ("exchange_name", "exchange"),
    "environment": ("environment", "env", "mode", "flag"),
    "levels": ("levels",),
}


@dataclass
class ParsedCLI:
    module: str
    module_roots: tuple[Path, ...]
    function: str
    values: Dict[str, object]
    params: Dict[str, object]


def _resolve_path(path_str: str) -> Path:
    path = Path(path_str)
    if not path.is_absolute():
        path = Path.cwd() / path
    return path.resolve()


def _load_module(module_name: str, search_paths: Iterable[Path]):
    for root in reversed(list(search_paths)):
        root_str = str(root)
        if root_str not in sys.path:
            sys.path.insert(0, root_str)
    return __import__(module_name, fromlist=["*"])


def _parse_environment(value: object, target_parameter: str) -> object:
    if value is None:
        return None
    if target_parameter == "flag":
        if isinstance(value, int):
            return value
        str_value = str(value).strip().lower()
        if str_value.isdigit():
            return int(str_value)
        if str_value in {"live", "production", "prod"}:
            return 0
        if str_value in {"demo", "paper", "paper-trade", "test"}:
            return 1
        raise ValueError(
            f"Unsupported environment value '{value}' for flag parameter"
        )
    return value


def _convert_value(name: str, value: object) -> object:
    if value is None:
        return None
    if name in {"limit", "levels"}:
        if isinstance(value, int):
            return value
        return int(str(value))
    return value


def _parse_params(values: Iterable[str]) -> Dict[str, object]:
    parsed: Dict[str, object] = {}
    for raw in values:
        if "=" not in raw:
            raise ValueError(
                "Invalid --param format. Expected key=value but received: " + raw
            )
        key, raw_value = raw.split("=", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        if not key:
            raise ValueError("Parameter name cannot be empty")
        try:
            value = ast.literal_eval(raw_value)
        except (SyntaxError, ValueError):
            value = raw_value
        parsed[key] = value
    return parsed


def _collect_cli(argv: Optional[Iterable[str]] = None) -> ParsedCLI:
    parser = argparse.ArgumentParser(description="Run legacy module entry-points")
    parser.add_argument("--module", required=True, help="Name of the module to import")
    parser.add_argument(
        "--module-root",
        action="append",
        default=[],
        dest="module_roots",
        help="Directory to add to sys.path prior to importing the module.",
    )
    parser.add_argument(
        "--function",
        default="run",
        help="Name of the function to invoke. Defaults to 'run'.",
    )
    parser.add_argument("--pair", help="Trading pair (e.g. BTCUSDT)")
    parser.add_argument("--interval", help="Time interval (e.g. 5m)")
    parser.add_argument("--limit", help="Data limit for historical requests")
    parser.add_argument("--levels", help="Order book depth levels")
    parser.add_argument(
        "--exchange",
        help="Exchange identifier (defaults to MT_EXCHANGE environment variable)",
    )
    parser.add_argument(
        "--environment",
        help=(
            "Runtime environment flag (e.g. live/demo). Defaults to MT_ENVIRONMENT "
            "environment variable if present."
        ),
    )
    parser.add_argument(
        "--param",
        action="append",
        default=[],
        help=(
            "Additional key=value pairs to forward as keyword arguments to the target "
            "function. Values are parsed using ast.literal_eval when possible."
        ),
    )

    args = parser.parse_args(list(argv) if argv is not None else None)

    env_defaults = {
        "pair": os.getenv("MT_PAIR"),
        "interval": os.getenv("MT_INTERVAL"),
        "limit": os.getenv("MT_LIMIT"),
        "levels": os.getenv("MT_LEVELS"),
        "exchange": os.getenv("MT_EXCHANGE"),
        "environment": os.getenv("MT_ENVIRONMENT"),
    }

    values: Dict[str, object] = {
        "pair": args.pair or env_defaults["pair"],
        "interval": args.interval or env_defaults["interval"],
        "limit": args.limit or env_defaults["limit"],
        "levels": args.levels or env_defaults["levels"],
        "exchange": args.exchange or env_defaults["exchange"],
        "environment": args.environment or env_defaults["environment"],
    }

    module_roots = tuple(_resolve_path(p) for p in args.module_roots)
    params = _parse_params(args.param)

    return ParsedCLI(
        module=args.module,
        module_roots=module_roots,
        function=args.function,
        values=values,
        params=params,
    )


def _build_call_arguments(
    func, parsed: ParsedCLI
) -> MutableMapping[str, object]:
    signature = inspect.signature(func)
    call_kwargs: Dict[str, object] = {}
    available = dict(parsed.values)

    for parameter in signature.parameters.values():
        if parameter.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue

        value = None
        selected_alias: Optional[str] = None
        for logical_name, aliases in ARGUMENT_ALIASES.items():
            if parameter.name in aliases:
                selected_alias = logical_name
                candidate = available.get(logical_name)
                if candidate is not None:
                    value = candidate
                break

        if value is None and parameter.name in parsed.params:
            value = parsed.params[parameter.name]

        if value is None:
            if parameter.default is inspect.Signature.empty:
                raise TypeError(
                    f"Missing required argument '{parameter.name}' for function {func.__name__}"
                )
            continue

        if selected_alias == "environment":
            value = _parse_environment(value, parameter.name)
        elif selected_alias is not None:
            value = _convert_value(selected_alias, value)

        call_kwargs[parameter.name] = value

    return call_kwargs


def main(argv: Optional[Iterable[str]] = None) -> None:
    parsed = _collect_cli(argv)
    module = _load_module(parsed.module, parsed.module_roots)
    if not hasattr(module, parsed.function):
        raise AttributeError(
            f"Module '{parsed.module}' does not expose callable '{parsed.function}'"
        )
    func = getattr(module, parsed.function)
    call_kwargs = _build_call_arguments(func, parsed)
    func(**call_kwargs)


if __name__ == "__main__":
    main()
