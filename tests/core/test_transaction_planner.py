from __future__ import annotations

from pathlib import Path

from workspace_fabric.config import load_config, load_config_text
from workspace_fabric.core.graph import build_resource_graph
from workspace_fabric.core.planner import USB_ROUTE_ACTION, VIDEO_ROUTE_ACTION, plan_workspace
from workspace_fabric.core.transactions import TransactionPlanStatus
from workspace_fabric.drivers.mock import MockVideoMatrixDriver, create_mock_drivers


def test_workspace_converts_to_transaction_plan_with_video_and_usb_actions() -> None:
    config = load_config(Path("examples/local-workspace.yaml"))
    graph = build_resource_graph(config)
    drivers = create_mock_drivers(config.drivers.values())

    plan = plan_workspace(graph, "hybrid_meeting", drivers, transaction_id="tx_test")

    assert plan.valid
    assert plan.id == "tx_test"
    assert plan.workspace_id == "hybrid_meeting"
    assert [action.action_type for action in plan.actions] == [
        VIDEO_ROUTE_ACTION,
        VIDEO_ROUTE_ACTION,
        USB_ROUTE_ACTION,
        USB_ROUTE_ACTION,
        USB_ROUTE_ACTION,
        USB_ROUTE_ACTION,
        USB_ROUTE_ACTION,
    ]
    assert plan.actions[0].driver_id == "mock_video"
    assert plan.actions[0].payload == {
        "source": "desktop_dp1",
        "destination": "primary_4k",
    }
    assert plan.actions[2].driver_id == "mock_usb_a"
    assert plan.actions[2].payload == {
        "device": "keyboard",
        "host": "desktop",
        "device_port": 1,
        "host_port": 1,
    }
    assert plan.actions[-1].driver_id == "mock_usb_b"
    assert plan.actions[-1].payload == {
        "device": "speakers",
        "host": "work_laptop",
        "device_port": 1,
        "host_port": 2,
    }


def test_transaction_plan_exposes_dry_run_output() -> None:
    config = load_config(Path("examples/local-workspace.yaml"))
    graph = build_resource_graph(config)
    drivers = create_mock_drivers(config.drivers.values())

    plan = plan_workspace(graph, "desktop", drivers, transaction_id="tx_dry_run")
    output = plan.dry_run_output()

    assert output["transaction"]["id"] == "tx_dry_run"
    assert output["transaction"]["workspace"] == "desktop"
    assert output["transaction"]["status"] == TransactionPlanStatus.PLANNED
    assert output["transaction"]["dry_run"] is True
    assert output["transaction"]["actions"][0] == {
        "driver": "mock_video",
        "type": "video_route",
        "path": "$.workspaces.desktop.video.primary_4k",
        "status": "planned",
        "steps": ["route video source 'desktop_dp1' to 'primary_4k'"],
        "source": "desktop_dp1",
        "destination": "primary_4k",
    }
    assert output["transaction"]["warnings"] == []
    assert output["transaction"]["errors"] == []


def test_transaction_plan_includes_optional_capability_warnings() -> None:
    config = load_config(Path("examples/local-workspace.yaml"))
    graph = build_resource_graph(config)
    drivers = create_mock_drivers(config.drivers.values())
    drivers["mock_video"] = MockVideoMatrixDriver(
        "mock_video",
        capabilities={"fast_switching": "unsupported"},
    )

    plan = plan_workspace(graph, "hybrid_meeting", drivers, transaction_id="tx_warning")
    output = plan.dry_run_output()

    assert plan.valid
    assert len(plan.actions) == 7
    assert plan.warnings[0].category == "unsupported_capability"
    assert plan.warnings[0].driver_id == "mock_video"
    assert output["transaction"]["warnings"][0]["category"] == "unsupported_capability"
    assert output["transaction"]["warnings"][0]["path"] == (
        "$.workspaces.hybrid_meeting.video.primary_4k.fast_switching"
    )


def test_transaction_plan_fails_when_required_capability_is_unknown() -> None:
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

    plan = plan_workspace(graph, "desktop", drivers, transaction_id="tx_failed")

    assert not plan.valid
    assert plan.status == TransactionPlanStatus.FAILED_VALIDATION
    assert plan.actions == ()
    assert plan.errors[0].category == "unknown_capability"
    assert plan.dry_run_output()["transaction"]["status"] == "failed_validation"


def test_transaction_plan_reports_missing_driver_instances() -> None:
    config = load_config(Path("examples/local-workspace.yaml"))
    graph = build_resource_graph(config)
    drivers = create_mock_drivers(config.drivers.values())
    del drivers["mock_usb_b"]

    plan = plan_workspace(graph, "desktop", drivers, transaction_id="tx_missing_driver")

    assert not plan.valid
    assert any(error.category == "missing_driver" for error in plan.errors)
    assert any(error.driver_id == "mock_usb_b" for error in plan.errors)
