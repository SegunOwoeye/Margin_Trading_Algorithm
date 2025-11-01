"""Core data structures used by the orchestrator runtime."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence


@dataclass
class CommandSpec:
    """Representation of a process to launch.

    Attributes
    ----------
    command:
        Full command invocation represented as a sequence of strings. This is
        passed directly to :mod:`subprocess`.
    name:
        Optional human readable name that the orchestrator can use for logging
        or UI display purposes.
    env:
        Environment variable overrides specific to this command. These values
        are merged with the parent environment when the process is spawned.
    cwd:
        Optional working directory for the process. When omitted, the
        orchestrator will default to the repository root.
    tags:
        Arbitrary metadata that callers can use to categorise commands.
    """

    command: Sequence[str]
    name: Optional[str] = None
    env: Mapping[str, str] = field(default_factory=dict)
    cwd: Optional[Path] = None
    tags: Mapping[str, str] = field(default_factory=dict)

    def with_overrides(
        self,
        *,
        env: Optional[Mapping[str, str]] = None,
        cwd: Optional[Path] = None,
        name: Optional[str] = None,
        tags: Optional[Mapping[str, str]] = None,
    ) -> "CommandSpec":
        """Return a copy of the command with updated attributes."""

        merged_env: Dict[str, str] = dict(self.env)
        if env:
            merged_env.update(env)

        merged_tags: Dict[str, str] = dict(self.tags)
        if tags:
            merged_tags.update(tags)

        return CommandSpec(
            command=list(self.command),
            name=name or self.name,
            env=merged_env,
            cwd=cwd or self.cwd,
            tags=merged_tags,
        )

    @property
    def argv(self) -> List[str]:
        return list(self.command)

    def describe(self) -> str:
        label = self.name or "Command"
        return f"{label}: {' '.join(self.command)}"
