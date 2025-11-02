"""Streamlit UI for orchestrating the legacy trading runtime."""
from __future__ import annotations

import sys
from typing import Iterable, List

import streamlit as st

from orchestration.command import CommandSpec
from orchestration.plans import RuntimePlan
from orchestration.process_manager import ProcessManager

PYTHON_EXECUTABLE = sys.executable or "python"


def _get_process_manager() -> ProcessManager:
    if "process_manager" not in st.session_state:
        st.session_state["process_manager"] = ProcessManager()
    return st.session_state["process_manager"]


def _get_runtime_plan() -> RuntimePlan:
    if "runtime_plan" not in st.session_state:
        st.session_state["runtime_plan"] = RuntimePlan.from_config()
    return st.session_state["runtime_plan"]


def _clone_with_python(spec: CommandSpec) -> CommandSpec:
    argv = list(spec.argv)
    if argv and argv[0] == "python":
        argv[0] = PYTHON_EXECUTABLE
    return CommandSpec(
        command=argv,
        name=spec.name,
        env=dict(spec.env),
        cwd=spec.cwd,
        tags=dict(spec.tags),
    )


def _normalised_commands(commands: Iterable[CommandSpec]) -> List[CommandSpec]:
    return [_clone_with_python(spec) for spec in commands]


def _update_running_commands(manager: ProcessManager) -> None:
    descriptions = [proc.spec.describe() for proc in manager.processes]
    st.session_state["running_processes"] = descriptions


def run_programs() -> None:
    manager = _get_process_manager()
    plan = _get_runtime_plan()
    manager.prune()
    if manager.processes:
        st.warning("Processes are already running. Terminate them before starting a new batch.")
        return

    commands = _normalised_commands(plan.commands())
    if not commands:
        st.error("No commands were generated from the current strategy plan.")
        return

    manager.launch(commands)
    _update_running_commands(manager)
    st.success(f"Launched {len(commands)} commands.")


def terminate_programs() -> None:
    manager = _get_process_manager()
    manager.terminate_all()
    manager.prune()
    _update_running_commands(manager)
    st.info("Termination signal sent to all running processes.")


def reload_plan() -> None:
    st.session_state["runtime_plan"] = RuntimePlan.from_config()
    st.success("Reloaded configuration from disk.")


st.title("Run Files")
with st.container():
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Run Bot"):
            run_programs()

    with col2:
        if st.button("Terminate Bot"):
            terminate_programs()

    with col3:
        if st.button("Reload Plan"):
            reload_plan()

plan = _get_runtime_plan()

st.subheader("Planned Commands")
for group, commands in plan.command_groups().items():
    with st.expander(group.replace("_", " ").title(), expanded=False):
        for spec in commands:
            st.code(_clone_with_python(spec).describe())

running = st.session_state.get("running_processes", [])
if running:
    st.subheader("Running Processes")
    for description in running:
        st.code(description)
else:
    st.caption("No processes are currently running.")
