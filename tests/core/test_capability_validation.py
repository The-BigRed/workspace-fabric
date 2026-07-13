from __future__ import annotations

from pathlib import Path

import pytest

from workspace_fabric.config import load_config, load_config_text
from workspace_fabric.core.capabilities import (
    CapabilityDecisionAction,
    CapabilityPolicy,
    CapabilityRequest,
    CapabilityStatus,
    validate_capability_request,
    validate_workspace_capabilities,
)
from workspace_fabric.core.graph import build_resource_graph
from workspace_fabric_driver_mock import (
    MockVideoMatrixDriver,
    create_mock_drivers,
)


def test_supported_prefer_and_require_capabilities_apply() -> None:
    capabilities = {"fast_switching": "supported"}

    prefer_result = validate_capability_request(
        capabilities,
        CapabilityRequest("fast_switching", policy=CapabilityPolicy.PREFER),
        driver_id="mock_video",
    )
    require_result = validate_capability_request(
        capabilities,
        CapabilityRequest("fast_switching", policy=CapabilityPolicy.REQUIRE),
        driver_id="mock_video",
    )

    assert prefer_result.valid
    assert require_result.valid
    assert prefer_result.decisions[0].action == CapabilityDecisionAction.APPLY
    assert require_result.decisions[0].action == CapabilityDecisionAction.APPLY
    assert not prefer_result.warnings
    assert not require_result.warnings


@pytest.mark.parametrize(
    ("capabilities", "expected_status", "expected_category"),
    [
        (
            {"fast_switching": "unsupported"},
            CapabilityStatus.UNSUPPORTED,
            "unsupported_capability",
        ),
        ({}, CapabilityStatus.UNKNOWN, "unknown_capability"),
    ],
)
def test_prefer_warns_when_capability_is_unsupported_or_unknown(
    capabilities: dict[str, str],
    expected_status: CapabilityStatus,
    expected_category: str,
) -> None:
    result = validate_capability_request(
        capabilities,
        CapabilityRequest("fast_switching", policy=CapabilityPolicy.PREFER),
        driver_id="mock_video",
    )

    assert result.valid
    assert result.warnings[0].category == expected_category
    assert result.decisions[0].status == expected_status
    assert result.decisions[0].action == CapabilityDecisionAction.IGNORE


@pytest.mark.parametrize(
    ("capabilities", "expected_status", "expected_category"),
    [
        (
            {"fast_switching": "unsupported"},
            CapabilityStatus.UNSUPPORTED,
            "unsupported_capability",
        ),
        ({}, CapabilityStatus.UNKNOWN, "unknown_capability"),
    ],
)
def test_require_fails_when_capability_is_unsupported_or_unknown(
    capabilities: dict[str, str],
    expected_status: CapabilityStatus,
    expected_category: str,
) -> None:
    result = validate_capability_request(
        capabilities,
        CapabilityRequest("fast_switching", policy=CapabilityPolicy.REQUIRE),
        driver_id="mock_video",
    )

    assert not result.valid
    assert result.errors[0].category == expected_category
    assert result.decisions[0].status == expected_status
    assert result.decisions[0].action == CapabilityDecisionAction.BLOCK


def test_ignore_and_disable_policies_are_supported() -> None:
    ignore_result = validate_capability_request(
        {"fast_switching": "unsupported"},
        CapabilityRequest("fast_switching", policy=CapabilityPolicy.IGNORE),
        driver_id="mock_video",
    )
    disable_result = validate_capability_request(
        {"fast_switching": "supported"},
        CapabilityRequest("fast_switching", policy=CapabilityPolicy.DISABLE),
        driver_id="mock_video",
    )

    assert ignore_result.valid
    assert disable_result.valid
    assert not ignore_result.warnings
    assert not ignore_result.errors
    assert ignore_result.decisions[0].action == CapabilityDecisionAction.IGNORE
    assert disable_result.decisions[0].action == CapabilityDecisionAction.DISABLE


def test_workspace_validation_queries_mock_driver_capabilities() -> None:
    config = load_config(Path("examples/local-workspace.yaml"))
    graph = build_resource_graph(config)
    drivers = create_mock_drivers(config.drivers.values())

    result = validate_workspace_capabilities(graph, "hybrid_meeting", drivers)

    assert result.valid
    assert not result.warnings
    assert result.decisions[0].capability == "fast_switching"
    assert result.decisions[0].driver_id == "mock_video"
    assert result.decisions[0].action == CapabilityDecisionAction.APPLY


def test_workspace_prefer_warns_when_mock_driver_reports_unsupported_capability() -> None:
    config = load_config(Path("examples/local-workspace.yaml"))
    graph = build_resource_graph(config)
    drivers = create_mock_drivers(config.drivers.values())
    drivers["mock_video"] = MockVideoMatrixDriver(
        "mock_video",
        capabilities={"fast_switching": "unsupported"},
    )

    result = validate_workspace_capabilities(graph, "hybrid_meeting", drivers)

    assert result.valid
    assert result.warnings[0].category == "unsupported_capability"
    assert result.warnings[0].path == "$.workspaces.hybrid_meeting.video.primary_4k.fast_switching"
    assert result.decisions[0].action == CapabilityDecisionAction.IGNORE


def test_workspace_require_fails_when_mock_driver_reports_unknown_capability() -> None:
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

    result = validate_workspace_capabilities(graph, "desktop", drivers)

    assert not result.valid
    assert result.errors[0].category == "unknown_capability"
    assert result.errors[0].path == "$.workspaces.desktop.video.primary_4k.fast_switching"
    assert result.decisions[0].action == CapabilityDecisionAction.BLOCK
