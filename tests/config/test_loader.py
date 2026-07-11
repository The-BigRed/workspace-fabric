from __future__ import annotations

from pathlib import Path

import pytest

from workspace_fabric.config import ConfigValidationError, load_config, load_config_text


def test_loads_example_configuration() -> None:
    config = load_config(Path("examples/local-workspace.yaml"))

    assert config.version == 1
    assert set(config.fabrics) == {"local_workspace"}
    assert set(config.drivers) == {"mock_video", "mock_usb_a", "mock_usb_b"}
    assert set(config.hosts) == {
        "desktop",
        "work_laptop",
        "pikvm",
        "controller",
        "spare_laptop",
        "rack_server",
    }
    assert set(config.displays) == {"primary_4k", "secondary_2k"}
    assert set(config.usb_matrices) == {"usb_a", "usb_b"}
    assert set(config.usb_devices) == {"keyboard", "mouse", "camera", "microphone", "speakers"}
    assert set(config.workspaces) == {"work", "desktop", "hybrid_meeting"}


def test_loads_physical_lab_configuration() -> None:
    config = load_config(Path("examples/physical-local.yaml"))

    assert config.version == 1
    assert set(config.fabrics) == {"physical_lab"}
    assert set(config.drivers) == {
        "video_matrix_uhd808",
        "usb_matrix_ukm404_a",
        "usb_matrix_ukm404_b",
    }
    assert config.drivers["video_matrix_uhd808"].type == "orei_uhd808"
    assert config.drivers["usb_matrix_ukm404_a"].type == "orei_ukm404"
    assert set(config.displays) == {"primary_4k", "secondary_2k", "pikvm_capture"}
    assert set(config.usb_matrices) == {"ukm404_a", "ukm404_b"}
    assert set(config.usb_devices) == {
        "primary_keyboard",
        "primary_mouse",
        "secondary_keyboard",
        "secondary_mouse",
        "webcam",
        "drop_mic",
        "fingerprint_reader",
        "pikvm_keyboard_mouse_hid",
    }
    assert {"desktop", "work", "hybrid_meeting"} <= set(config.workspaces)


def test_normalizes_workspace_video_shorthand_and_capability_requests() -> None:
    config = load_config(Path("examples/local-workspace.yaml"))

    work_primary = config.workspaces["work"].video["primary_4k"]
    assert work_primary.source == "work_laptop_dp1"
    assert work_primary.capabilities == {}

    hybrid_primary = config.workspaces["hybrid_meeting"].video["primary_4k"]
    assert hybrid_primary.source == "desktop_dp1"
    assert hybrid_primary.capabilities["fast_switching"].policy == "prefer"
    assert hybrid_primary.capabilities["fast_switching"].options == {
        "enabled": True,
        "policy": "prefer",
    }


def test_missing_version_fails_clearly() -> None:
    with pytest.raises(ConfigValidationError) as exc_info:
        load_config_text("fabrics: {}\n")

    assert "$.version: Required field is missing" in str(exc_info.value)


def test_unsupported_version_fails_clearly() -> None:
    with pytest.raises(ConfigValidationError) as exc_info:
        load_config_text("version: 2\n")

    assert "$.version: Unsupported schema version 2; expected 1" in str(exc_info.value)


def test_section_must_be_mapping() -> None:
    with pytest.raises(ConfigValidationError) as exc_info:
        load_config_text("""
            version: 1
            hosts: []
            """)

    assert "$.hosts: Expected a mapping of IDs to definitions" in str(exc_info.value)


def test_required_fields_are_validated() -> None:
    with pytest.raises(ConfigValidationError) as exc_info:
        load_config_text("""
            version: 1
            drivers:
              mock_video:
                fabric: local_workspace
            """)

    assert "$.drivers.mock_video.type: Required field is missing" in str(exc_info.value)


def test_driver_capability_status_must_be_known() -> None:
    with pytest.raises(ConfigValidationError) as exc_info:
        load_config_text("""
            version: 1
            drivers:
              mock_video:
                type: mock_video_matrix
                fabric: local_workspace
                capabilities:
                  video_routing: maybe
            """)

    assert "$.drivers.mock_video.capabilities.video_routing" in str(exc_info.value)
    assert "Unknown capability status 'maybe'" in str(exc_info.value)


def test_workspace_capability_policy_must_be_known() -> None:
    with pytest.raises(ConfigValidationError) as exc_info:
        load_config_text("""
            version: 1
            workspaces:
              desktop:
                fabric: local_workspace
                video:
                  primary_4k:
                    source: desktop_dp1
                    fast_switching:
                      enabled: true
                      policy: maybe
            """)

    assert "$.workspaces.desktop.video.primary_4k.fast_switching.policy" in str(exc_info.value)
    assert "Unknown capability policy 'maybe'" in str(exc_info.value)


def test_duplicate_yaml_keys_fail_clearly() -> None:
    with pytest.raises(ConfigValidationError) as exc_info:
        load_config_text("""
            version: 1
            fabrics:
              local_workspace: {}
              local_workspace: {}
            """)

    assert "duplicate key 'local_workspace'" in str(exc_info.value)


def test_usb_host_ports_are_normalized_to_integers() -> None:
    config = load_config_text("""
        version: 1
        usb_matrices:
          usb_a:
            fabric: local_workspace
            driver: mock_usb
            hosts:
              "1": desktop
              2: work_laptop
        """)

    assert config.usb_matrices["usb_a"].hosts == {
        1: "desktop",
        2: "work_laptop",
    }


def test_video_source_can_declare_driver_input_port() -> None:
    config = load_config_text("""
        version: 1
        video_sources:
          desktop_dp1:
            fabric: local_workspace
            host: desktop
            driver: uhd808
            port: 1
        """)

    source = config.video_sources["desktop_dp1"]

    assert source.driver == "uhd808"
    assert source.port == 1
