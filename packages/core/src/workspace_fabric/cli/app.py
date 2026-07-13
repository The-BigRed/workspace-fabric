from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import dataclass, field
from json import JSONDecodeError
from pathlib import Path
from typing import Any, TextIO

from workspace_fabric.config import ConfigValidationError, WorkspaceFabricConfig, load_config
from workspace_fabric.core.graph import ResourceGraph, ResourceGraphError, build_resource_graph
from workspace_fabric.core.planner import plan_workspace
from workspace_fabric.core.transactions import InMemoryTransactionHistory, TransactionExecutor
from workspace_fabric.drivers import (
    Driver,
    DriverAction,
    create_drivers,
    is_mock_driver_type,
    validate_driver_configuration,
)

DEFAULT_CONFIG_PATH = Path("examples/local-workspace.yaml")
DEFAULT_STATE_PATH = Path("runtime/state/workspace-fabric-mock-state.json")
STATE_SCHEMA_VERSION = 1
ACTION_METADATA_KEYS = frozenset(
    {
        "driver",
        "errors",
        "index",
        "observed_state",
        "path",
        "status",
        "type",
        "warnings",
    }
)


def main(argv: Sequence[str] | None = None) -> int:
    return WorkspaceFabricCLI().run(argv)


@dataclass
class WorkspaceFabricRuntime:
    config_path: Path = DEFAULT_CONFIG_PATH
    state_path: Path = DEFAULT_STATE_PATH
    history: InMemoryTransactionHistory = field(default_factory=InMemoryTransactionHistory)
    _config: WorkspaceFabricConfig | None = field(default=None, init=False)
    _graph: ResourceGraph | None = field(default=None, init=False)
    _drivers: dict[str, Driver] | None = field(default=None, init=False)
    _transactions: list[dict[str, Any]] | None = field(default=None, init=False)

    def configure(self, config_path: Path, state_path: Path) -> None:
        if config_path != self.config_path or state_path != self.state_path:
            self.config_path = config_path
            self.state_path = state_path
            self._config = None
            self._graph = None
            self._drivers = None
            self._transactions = None
            self.history.clear()

    @property
    def config(self) -> WorkspaceFabricConfig:
        self._load_config_graph()
        assert self._config is not None
        return self._config

    @property
    def graph(self) -> ResourceGraph:
        self._load_config_graph()
        assert self._graph is not None
        return self._graph

    @property
    def drivers(self) -> dict[str, Driver]:
        self._load_drivers()
        assert self._drivers is not None
        return self._drivers

    def state(self) -> dict[str, Any]:
        self._load_drivers()
        assert self._transactions is not None
        return {
            "drivers": {
                driver_id: dict(driver.get_state())
                for driver_id, driver in sorted(self.drivers.items())
            },
            "transactions": [
                {
                    "id": transaction["id"],
                    "workspace": transaction["workspace"],
                    "status": transaction["status"],
                    "recorded_at": transaction.get("recorded_at"),
                }
                for transaction in self._transactions
            ],
        }

    def record_apply_result(self, result: Any) -> None:
        self._load_drivers()
        assert self._transactions is not None

        transaction = result.dump()["transaction"]
        self._transactions.append(transaction)
        _write_state_file(
            self.state_path,
            {
                "version": STATE_SCHEMA_VERSION,
                "config_path": str(self.config_path),
                "transactions": self._transactions,
            },
        )

    def _load_config_graph(self) -> None:
        if self._config is not None and self._graph is not None:
            return

        config = load_config(self.config_path)
        graph = build_resource_graph(config)
        validate_driver_configuration(config.drivers.values())

        self._config = config
        self._graph = graph

    def _load_drivers(self) -> None:
        if (
            self._config is not None
            and self._graph is not None
            and self._drivers is not None
            and self._transactions is not None
        ):
            return

        self._load_config_graph()
        assert self._config is not None
        drivers = create_drivers(self._config.drivers.values())
        transactions = _transactions_for_config(
            _load_state_file(self.state_path),
            self.config_path,
        )
        replay_driver_ids = {
            config.id
            for config in self._config.drivers.values()
            if is_mock_driver_type(config.type)
        }
        _replay_transactions(drivers, transactions, replay_driver_ids)

        self._drivers = drivers
        self._transactions = transactions


class WorkspaceFabricCLI:
    def __init__(self, runtime: WorkspaceFabricRuntime | None = None) -> None:
        self._runtime = runtime or WorkspaceFabricRuntime()

    def run(
        self,
        argv: Sequence[str] | None = None,
        *,
        stdout: TextIO | None = None,
        stderr: TextIO | None = None,
    ) -> int:
        output = stdout or sys.stdout
        error_output = stderr or sys.stderr
        parser = build_parser()
        args = parser.parse_args(argv)

        try:
            self._runtime.configure(Path(args.config), Path(args.state_file))
            return self._run_command(args, output)
        except (ConfigValidationError, ResourceGraphError, ValueError) as exc:
            _write_json(error_output, {"error": {"message": str(exc)}})
            return 1

    def _run_command(self, args: argparse.Namespace, stdout: TextIO) -> int:
        match args.command:
            case "config":
                return self._run_config(args, stdout)
            case "graph":
                return self._run_graph(args, stdout)
            case "workspace":
                return self._run_workspace(args, stdout)
            case "apply":
                return self._run_apply(args, stdout)
            case "state":
                return self._run_state(stdout)
            case _:
                raise ValueError(f"Unsupported command {args.command!r}")

    def _run_config(self, args: argparse.Namespace, stdout: TextIO) -> int:
        if args.config_command != "validate":
            raise ValueError(f"Unsupported config command {args.config_command!r}")

        config = self._runtime.config
        graph = self._runtime.graph
        _write_json(
            stdout,
            {
                "config": {
                    "path": str(self._runtime.config_path),
                    "valid": True,
                    "version": config.version,
                    "resources": len(graph.nodes),
                    "relationships": len(graph.edges),
                }
            },
        )
        return 0

    def _run_graph(self, args: argparse.Namespace, stdout: TextIO) -> int:
        if args.graph_command != "show":
            raise ValueError(f"Unsupported graph command {args.graph_command!r}")

        _write_json(stdout, {"graph": self._runtime.graph.dump()})
        return 0

    def _run_workspace(self, args: argparse.Namespace, stdout: TextIO) -> int:
        if args.workspace_command != "list":
            raise ValueError(f"Unsupported workspace command {args.workspace_command!r}")

        _write_json(
            stdout,
            {
                "workspaces": [
                    {
                        "id": workspace.id,
                        "display_name": workspace.display_name,
                    }
                    for workspace in sorted(
                        self._runtime.config.workspaces.values(),
                        key=lambda workspace: workspace.id,
                    )
                ]
            },
        )
        return 0

    def _run_apply(self, args: argparse.Namespace, stdout: TextIO) -> int:
        plan = plan_workspace(
            self._runtime.graph,
            args.workspace_id,
            self._runtime.drivers,
        )
        if args.dry_run:
            _write_json(stdout, plan.dry_run_output())
            return 0 if plan.valid else 1

        result = TransactionExecutor(
            self._runtime.drivers,
            history=self._runtime.history,
        ).execute(plan)
        self._runtime.record_apply_result(result)
        _write_json(stdout, result.dump())
        return 0 if result.successful else 1

    def _run_state(self, stdout: TextIO) -> int:
        _write_json(stdout, {"state": self._runtime.state()})
        return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="workspace-fabric",
        description="Workspace Fabric control plane CLI.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    config_parser = subcommands.add_parser("config", help="Configuration commands.")
    config_subcommands = config_parser.add_subparsers(dest="config_command", required=True)
    config_validate_parser = config_subcommands.add_parser(
        "validate",
        help="Validate the workspace configuration.",
    )
    _add_runtime_arguments(config_validate_parser)

    graph_parser = subcommands.add_parser("graph", help="Resource graph commands.")
    graph_subcommands = graph_parser.add_subparsers(dest="graph_command", required=True)
    graph_show_parser = graph_subcommands.add_parser(
        "show", help="Show the resolved resource graph."
    )
    _add_runtime_arguments(graph_show_parser)

    workspace_parser = subcommands.add_parser("workspace", help="Workspace commands.")
    workspace_subcommands = workspace_parser.add_subparsers(
        dest="workspace_command",
        required=True,
    )
    workspace_list_parser = workspace_subcommands.add_parser(
        "list", help="List configured workspaces."
    )
    _add_runtime_arguments(workspace_list_parser)

    apply_parser = subcommands.add_parser("apply", help="Apply a workspace.")
    _add_runtime_arguments(apply_parser)
    apply_parser.add_argument("workspace_id", metavar="workspace")
    apply_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without applying; recommended before physical hardware apply.",
    )

    state_parser = subcommands.add_parser("state", help="Show observed driver state.")
    _add_runtime_arguments(state_parser)

    return parser


def _add_runtime_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help=f"Path to workspace YAML configuration. Defaults to {DEFAULT_CONFIG_PATH}.",
    )
    parser.add_argument(
        "--state-file",
        default=str(DEFAULT_STATE_PATH),
        help=f"Path to persisted mock state. Defaults to {DEFAULT_STATE_PATH}.",
    )


def _write_json(stream: TextIO, data: dict[str, Any]) -> None:
    json.dump(data, stream, indent=2, sort_keys=True)
    stream.write("\n")


def _load_state_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "version": STATE_SCHEMA_VERSION,
            "config_path": "",
            "transactions": [],
        }

    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"Could not read state file {path}: {exc}") from exc
    except JSONDecodeError as exc:
        raise ValueError(f"State file {path} is not valid JSON: {exc}") from exc

    if not isinstance(state, dict):
        raise ValueError(f"State file {path} must contain a JSON object")
    if state.get("version") != STATE_SCHEMA_VERSION:
        raise ValueError(
            f"State file {path} uses unsupported version {state.get('version')!r}; "
            f"expected {STATE_SCHEMA_VERSION}"
        )
    transactions = state.get("transactions", [])
    if not isinstance(transactions, list) or not all(
        isinstance(transaction, dict) for transaction in transactions
    ):
        raise ValueError(f"State file {path} transactions must be a list of objects")

    return state


def _write_state_file(path: Path, state: dict[str, Any]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"Could not write state file {path}: {exc}") from exc


def _transactions_for_config(state: dict[str, Any], config_path: Path) -> list[dict[str, Any]]:
    configured_path = state.get("config_path")
    if configured_path and configured_path != str(config_path):
        return []
    return list(state["transactions"])


def _replay_transactions(
    drivers: dict[str, Driver],
    transactions: list[dict[str, Any]],
    replay_driver_ids: set[str],
) -> None:
    for transaction in transactions:
        for action in transaction.get("actions", []):
            if not isinstance(action, dict) or action.get("status") != "success":
                continue

            driver_id = str(action.get("driver"))
            if driver_id not in replay_driver_ids:
                continue

            driver = drivers.get(driver_id)
            action_type = action.get("type")
            if driver is None or not isinstance(action_type, str):
                continue

            driver.apply_action(
                DriverAction(
                    action_type=action_type,
                    payload={
                        key: value
                        for key, value in action.items()
                        if key not in ACTION_METADATA_KEYS
                    },
                )
            )
