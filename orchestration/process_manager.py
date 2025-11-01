"""Utilities for launching and supervising the strategy subprocesses."""
from __future__ import annotations

import os
import signal
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

from .command import CommandSpec


@dataclass
class ManagedProcess:
    spec: CommandSpec
    process: subprocess.Popen

    def terminate(self) -> None:
        if self.process.poll() is None:
            self.process.terminate()

    def kill(self) -> None:
        if self.process.poll() is None:
            self.process.kill()


class ProcessManager:
    """Launch and manage the lifecycle of the configured command set."""

    def __init__(self, *, default_cwd: Optional[Path] = None) -> None:
        self._default_cwd = default_cwd or Path.cwd()
        self._processes: List[ManagedProcess] = []

    @property
    def processes(self) -> Sequence[ManagedProcess]:
        return list(self._processes)

    def launch(self, commands: Iterable[CommandSpec]) -> Sequence[ManagedProcess]:
        launched: List[ManagedProcess] = []
        for spec in commands:
            env = os.environ.copy()
            env.update(spec.env)
            cwd = spec.cwd or self._default_cwd
            proc = subprocess.Popen(spec.argv, cwd=cwd, env=env)
            managed = ManagedProcess(spec=spec, process=proc)
            self._processes.append(managed)
            launched.append(managed)
        return launched

    def terminate_all(self, *, wait: bool = False) -> None:
        for managed in self._processes:
            managed.terminate()
        if wait:
            for managed in self._processes:
                managed.process.wait()

    def kill_all(self) -> None:
        for managed in self._processes:
            managed.kill()

    def send_signal(self, sig: int = signal.SIGTERM) -> None:
        for managed in self._processes:
            if managed.process.poll() is None:
                managed.process.send_signal(sig)

    def prune(self) -> None:
        """Remove entries for processes that have already exited."""

        self._processes = [p for p in self._processes if p.process.poll() is None]
