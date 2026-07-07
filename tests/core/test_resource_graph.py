from __future__ import annotations

from pathlib import Path

import pytest

from workspace_fabric.config import load_config, load_config_text
from workspace_fabric.config.models import FabricConfig, HostConfig, WorkspaceFabricConfig
from workspace_fabric.core.graph import ResourceGraphError, ResourceKind, build_resource_graph


def test_builds_graph_from_example_configuration() -> None:
    config = load_config(Path("examples/local-workspace.yaml"))

    graph = build_resource_graph(config)

    assert graph.get_node(ResourceKind.DISPLAY, "primary_4k") is not None
    assert graph.get_node(ResourceKind.USB_DEVICE, "keyboard") is not None
    assert graph.resolve_video_route("primary_4k", "desktop_dp1").driver.id == "mock_video"
    assert graph.resolve_usb_route("speakers", "controller").driver.id == "mock_usb_b"


def test_per_matrix_usb_host_maps_are_represented_independently() -> None:
    graph = build_resource_graph(load_config(Path("examples/local-workspace.yaml")))

    assert graph.usb_host_map("usb_a") == {
        1: "desktop",
        2: "work_laptop",
        3: "pikvm",
        4: "spare_laptop",
    }
    assert graph.usb_host_map("usb_b") == {
        1: "desktop",
        2: "work_laptop",
        3: "controller",
        4: "rack_server",
    }


def test_invalid_usb_route_targets_are_detectable() -> None:
    graph = build_resource_graph(load_config(Path("examples/local-workspace.yaml")))

    assert graph.can_route_usb_device_to_host("speakers", "controller")
    assert not graph.can_route_usb_device_to_host("camera", "controller")

    with pytest.raises(ResourceGraphError) as exc_info:
        graph.resolve_usb_route("camera", "controller")

    assert "Host 'controller' is not attached to USB matrix 'usb_a'" in str(exc_info.value)


def test_graph_dump_includes_resources_and_relationships() -> None:
    graph = build_resource_graph(load_config(Path("examples/local-workspace.yaml")))

    dump = graph.dump()

    assert dump["resources"]["fabrics"] == ["local_workspace"]
    assert dump["relationships"]["displays"]["primary_4k"] == {
        "output": "video_out1",
        "driver": "mock_video",
    }
    assert dump["relationships"]["usb_devices"]["speakers"] == {
        "matrix": "usb_b",
        "device_port": 1,
        "driver": "mock_usb_b",
    }


def test_missing_references_fail_graph_validation() -> None:
    config = load_config_text("""
        version: 1
        fabrics:
          local_workspace: {}
        displays:
          primary_4k:
            fabric: local_workspace
            output: missing_output
        """)

    with pytest.raises(ResourceGraphError) as exc_info:
        build_resource_graph(config)

    assert "$.displays.primary_4k.output" in str(exc_info.value)
    assert "Unknown video output reference 'missing_output'" in str(exc_info.value)


def test_duplicate_ids_fail_graph_validation() -> None:
    config = WorkspaceFabricConfig(
        version=1,
        fabrics={"local_workspace": FabricConfig(id="local_workspace")},
        hosts={
            "desktop": HostConfig(id="duplicate_host", fabric="local_workspace"),
            "work_laptop": HostConfig(id="duplicate_host", fabric="local_workspace"),
        },
    )

    with pytest.raises(ResourceGraphError) as exc_info:
        build_resource_graph(config)

    assert "Duplicate host ID 'duplicate_host'" in str(exc_info.value)


def test_configured_invalid_usb_workspace_route_fails_graph_validation() -> None:
    config = load_config_text("""
        version: 1
        fabrics:
          local_workspace: {}
        drivers:
          mock_usb:
            type: mock_usb_matrix
            fabric: local_workspace
        hosts:
          desktop:
            fabric: local_workspace
          controller:
            fabric: local_workspace
        usb_matrices:
          usb_a:
            fabric: local_workspace
            driver: mock_usb
            hosts:
              1: desktop
        usb_devices:
          keyboard:
            fabric: local_workspace
            matrix: usb_a
            device_port: 1
        workspaces:
          desktop:
            fabric: local_workspace
            usb:
              keyboard: controller
        """)

    with pytest.raises(ResourceGraphError) as exc_info:
        build_resource_graph(config)

    assert "$.workspaces.desktop.usb.keyboard" in str(exc_info.value)
    assert "Host 'controller' is not attached to USB matrix 'usb_a'" in str(exc_info.value)
