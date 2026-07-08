from __future__ import annotations

import json
from io import StringIO
from pathlib import Path
from typing import Any

from workspace_fabric.cli import WorkspaceFabricCLI


def run_cli(
    cli: WorkspaceFabricCLI,
    args: list[str],
    *,
    state_file: Path,
) -> tuple[int, dict[str, Any], str]:
    stdout = StringIO()
    stderr = StringIO()

    exit_code = cli.run(
        [*args, "--state-file", str(state_file)],
        stdout=stdout,
        stderr=stderr,
    )

    output = json.loads(stdout.getvalue()) if stdout.getvalue() else {}
    return exit_code, output, stderr.getvalue()


def test_config_validate_graph_show_and_workspace_list_commands(tmp_path: Path) -> None:
    cli = WorkspaceFabricCLI()
    state_file = tmp_path / "state.json"

    validate_code, validate_output, validate_error = run_cli(
        cli, ["config", "validate"], state_file=state_file
    )
    graph_code, graph_output, graph_error = run_cli(cli, ["graph", "show"], state_file=state_file)
    list_code, list_output, list_error = run_cli(cli, ["workspace", "list"], state_file=state_file)

    assert validate_code == 0
    assert validate_output["config"]["valid"] is True
    assert validate_output["config"]["version"] == 1
    assert validate_error == ""
    assert graph_code == 0
    assert "primary_4k" in graph_output["graph"]["resources"]["displays"]
    assert graph_error == ""
    assert list_code == 0
    assert [workspace["id"] for workspace in list_output["workspaces"]] == [
        "desktop",
        "hybrid_meeting",
        "work",
    ]
    assert list_error == ""


def test_apply_dry_run_returns_plan_without_updating_state(tmp_path: Path) -> None:
    cli = WorkspaceFabricCLI()
    state_file = tmp_path / "state.json"

    dry_run_code, dry_run_output, dry_run_error = run_cli(
        cli,
        ["apply", "hybrid_meeting", "--dry-run"],
        state_file=state_file,
    )
    state_code, state_output, state_error = run_cli(cli, ["state"], state_file=state_file)

    assert dry_run_code == 0
    assert dry_run_output["transaction"]["dry_run"] is True
    assert dry_run_output["transaction"]["workspace"] == "hybrid_meeting"
    assert len(dry_run_output["transaction"]["actions"]) == 7
    assert dry_run_error == ""
    assert state_code == 0
    assert state_output["state"]["drivers"]["mock_video"]["routes"] == {}
    assert state_output["state"]["transactions"] == []
    assert state_error == ""
    assert not state_file.exists()


def test_apply_documented_workspaces_and_view_resulting_state(tmp_path: Path) -> None:
    state_file = tmp_path / "state.json"

    for workspace_id in ("work", "desktop", "hybrid_meeting"):
        exit_code, output, error = run_cli(
            WorkspaceFabricCLI(),
            ["apply", workspace_id],
            state_file=state_file,
        )

        assert exit_code == 0
        assert output["transaction"]["workspace"] == workspace_id
        assert output["transaction"]["status"] == "success"
        assert error == ""

    state_code, state_output, state_error = run_cli(
        WorkspaceFabricCLI(),
        ["state"],
        state_file=state_file,
    )

    assert state_code == 0
    assert state_output["state"]["drivers"]["mock_video"]["routes"] == {
        "primary_4k": "desktop_dp1",
        "secondary_2k": "work_laptop_dp1",
    }
    assert state_output["state"]["drivers"]["mock_usb_a"]["routes"] == {
        "camera": "work_laptop",
        "keyboard": "desktop",
        "microphone": "work_laptop",
        "mouse": "desktop",
    }
    assert state_output["state"]["drivers"]["mock_usb_b"]["routes"] == {
        "speakers": "work_laptop",
    }
    assert [transaction["workspace"] for transaction in state_output["state"]["transactions"]] == [
        "work",
        "desktop",
        "hybrid_meeting",
    ]
    assert state_error == ""


def test_apply_then_state_persists_across_separate_cli_invocations(tmp_path: Path) -> None:
    state_file = tmp_path / "state.json"

    apply_code, apply_output, apply_error = run_cli(
        WorkspaceFabricCLI(),
        ["apply", "desktop"],
        state_file=state_file,
    )
    state_code, state_output, state_error = run_cli(
        WorkspaceFabricCLI(),
        ["state"],
        state_file=state_file,
    )

    assert apply_code == 0
    assert apply_output["transaction"]["status"] == "success"
    assert apply_error == ""
    assert state_file.exists()
    assert state_code == 0
    assert state_output["state"]["drivers"]["mock_video"]["routes"] == {
        "primary_4k": "desktop_dp1",
        "secondary_2k": "desktop_dp2",
    }
    assert state_output["state"]["drivers"]["mock_usb_a"]["routes"] == {
        "camera": "desktop",
        "keyboard": "desktop",
        "microphone": "desktop",
        "mouse": "desktop",
    }
    assert state_output["state"]["drivers"]["mock_usb_b"]["routes"] == {
        "speakers": "desktop",
    }
    assert state_output["state"]["transactions"][0]["workspace"] == "desktop"
    assert state_output["state"]["transactions"][0]["status"] == "success"
    assert state_error == ""


def test_apply_unknown_workspace_returns_validation_error(tmp_path: Path) -> None:
    cli = WorkspaceFabricCLI()
    state_file = tmp_path / "state.json"

    exit_code, output, error = run_cli(cli, ["apply", "missing_workspace"], state_file=state_file)

    assert exit_code == 1
    assert output["transaction"]["status"] == "failed_validation"
    assert output["transaction"]["errors"][0]["category"] == "unknown_workspace"
    assert error == ""
