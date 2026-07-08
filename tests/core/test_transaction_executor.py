from __future__ import annotations

from pathlib import Path

from workspace_fabric.config import load_config, load_config_text
from workspace_fabric.core.graph import build_resource_graph
from workspace_fabric.core.planner import plan_workspace
from workspace_fabric.core.transactions import (
    InMemoryTransactionHistory,
    TransactionExecutor,
    TransactionResultStatus,
    execute_plan,
)
from workspace_fabric.drivers import DriverActionStatus
from workspace_fabric.drivers.mock import create_mock_drivers


def test_execute_plan_against_mock_drivers_updates_state_and_records_history() -> None:
    config = load_config(Path("examples/local-workspace.yaml"))
    graph = build_resource_graph(config)
    drivers = create_mock_drivers(config.drivers.values())
    plan = plan_workspace(graph, "desktop", drivers, transaction_id="tx_execute")
    history = InMemoryTransactionHistory()

    result = execute_plan(plan, drivers, history=history)

    assert result.status == TransactionResultStatus.SUCCESS
    assert result.successful
    assert len(result.action_results) == 7
    assert drivers["mock_video"].get_state()["routes"] == {
        "primary_4k": "desktop_dp1",
        "secondary_2k": "desktop_dp2",
    }
    assert drivers["mock_usb_a"].get_state()["routes"] == {
        "keyboard": "desktop",
        "mouse": "desktop",
        "camera": "desktop",
        "microphone": "desktop",
    }
    assert drivers["mock_usb_b"].get_state()["routes"] == {"speakers": "desktop"}
    assert history.get("tx_execute") is result
    assert history.all() == (result,)


def test_transaction_execution_result_is_structured_and_dumpable() -> None:
    config = load_config(Path("examples/local-workspace.yaml"))
    graph = build_resource_graph(config)
    drivers = create_mock_drivers(config.drivers.values())
    plan = plan_workspace(graph, "work", drivers, transaction_id="tx_dump")

    result = execute_plan(plan, drivers)
    output = result.dump()

    assert output["transaction"]["id"] == "tx_dump"
    assert output["transaction"]["workspace"] == "work"
    assert output["transaction"]["status"] == "success"
    assert output["transaction"]["dry_run"] is False
    assert output["transaction"]["planned_actions"][0]["type"] == "video_route"
    assert output["transaction"]["actions"][0]["status"] == "success"
    assert output["transaction"]["actions"][0]["observed_state"]["routes"] == {
        "primary_4k": "work_laptop_dp1"
    }
    assert output["transaction"]["warnings"] == []
    assert output["transaction"]["errors"] == []
    assert "recorded_at" in output["transaction"]


def test_partial_failure_can_be_represented() -> None:
    config = load_config(Path("examples/local-workspace.yaml"))
    graph = build_resource_graph(config)
    drivers = create_mock_drivers(config.drivers.values())
    plan = plan_workspace(graph, "desktop", drivers, transaction_id="tx_partial")
    drivers["mock_usb_a"].fail_next_action("usb_route", "Injected USB routing failure")

    result = execute_plan(plan, drivers)

    assert result.status == TransactionResultStatus.PARTIAL_SUCCESS
    assert not result.successful
    assert any(
        action_result.status == DriverActionStatus.FAILED_APPLY
        for action_result in result.action_results
    )
    assert any(action_result.successful for action_result in result.action_results)
    assert result.errors[0].category == "mock_failure"
    assert result.errors[0].action_index == 2
    assert drivers["mock_video"].get_state()["routes"] == {
        "primary_4k": "desktop_dp1",
        "secondary_2k": "desktop_dp2",
    }
    assert "keyboard" not in drivers["mock_usb_a"].get_state()["routes"]
    assert drivers["mock_usb_a"].get_state()["routes"]["mouse"] == "desktop"


def test_failed_validation_plan_is_recorded_without_applying_actions() -> None:
    config = load_config_text("""
        version: 1
        fabrics:
          local_workspace: {}
        drivers:
          mock_video:
            type: mock_video_matrix
            fabric: local_workspace
            capabilities:
              video_routing: supported
        hosts:
          desktop:
            fabric: local_workspace
        video_sources:
          desktop_dp1:
            fabric: local_workspace
            host: desktop
        video_outputs:
          video_out1:
            fabric: local_workspace
            driver: mock_video
            port: 1
        displays:
          primary_4k:
            fabric: local_workspace
            output: video_out1
        workspaces:
          desktop:
            fabric: local_workspace
            video:
              primary_4k:
                source: desktop_dp1
                fast_switching:
                  policy: require
        """)
    graph = build_resource_graph(config)
    drivers = create_mock_drivers(config.drivers.values())
    plan = plan_workspace(graph, "desktop", drivers, transaction_id="tx_validation_failed")
    executor = TransactionExecutor(drivers)

    result = executor.execute(plan)

    assert result.status == TransactionResultStatus.FAILED_VALIDATION
    assert result.action_results == ()
    assert result.errors[0].category == "unknown_capability"
    assert drivers["mock_video"].get_state()["routes"] == {}
    assert executor.history.get("tx_validation_failed") is result


def test_missing_driver_during_execution_is_reported_as_failed_apply() -> None:
    config = load_config(Path("examples/local-workspace.yaml"))
    graph = build_resource_graph(config)
    planning_drivers = create_mock_drivers(config.drivers.values())
    plan = plan_workspace(graph, "desktop", planning_drivers, transaction_id="tx_missing_driver")
    execution_drivers = dict(planning_drivers)
    del execution_drivers["mock_video"]

    result = execute_plan(plan, execution_drivers)

    assert result.status == TransactionResultStatus.PARTIAL_SUCCESS
    assert result.action_results[0].status == DriverActionStatus.FAILED_APPLY
    assert result.action_results[0].errors[0].category == "missing_driver"
    assert result.errors[0].driver_id == "mock_video"
