from __future__ import annotations

import re
from pathlib import Path

from workspace_fabric.config import load_config
from workspace_fabric.core.graph import build_resource_graph
from workspace_fabric.core.planner import plan_workspace
from workspace_fabric.core.transactions import TransactionResultStatus, execute_plan
from workspace_fabric.drivers import Driver
from workspace_fabric.drivers.usb import OreiUkm404UsbDriver
from workspace_fabric.drivers.video import OreiUhd808VideoDriver

_UHD_ROUTE_PATTERN = re.compile(r"s in (\d+) av out (\d+)!")
_UKM_ROUTE_PATTERN = re.compile(r"set device (\d+) in host (\d+)")
_UKM_QUERY_PATTERN = re.compile(r"get device (\d+) in host")


class ScriptedUhd808Transport:
    def __init__(self) -> None:
        self.routes_by_output: dict[int, int] = {}
        self.commands: list[str] = []
        self.connected = False

    def connect(self) -> None:
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False

    def send_command(self, command: str, *, timeout_seconds: float | None = None) -> str:
        self.commands.append(command)

        if command == "r av out 0!":
            return "\n".join(
                f"input {input_port} -> output {output_port}"
                for output_port, input_port in sorted(self.routes_by_output.items())
            )

        route_match = _UHD_ROUTE_PATTERN.fullmatch(command)
        if route_match is None:
            raise AssertionError(f"Unexpected UHD-808 command {command!r}")

        input_port = int(route_match.group(1))
        output_port = int(route_match.group(2))
        self.routes_by_output[output_port] = input_port
        return f"input {input_port} -> output {output_port}"


class ScriptedUkm404Transport:
    def __init__(self) -> None:
        self.routes_by_device: dict[int, int] = {}
        self.commands: list[str] = []
        self.connected = False

    def connect(self) -> None:
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False

    def send_command(self, command: str, *, timeout_seconds: float | None = None) -> str:
        self.commands.append(command)

        route_match = _UKM_ROUTE_PATTERN.fullmatch(command)
        if route_match is not None:
            device_port = int(route_match.group(1))
            host_port = int(route_match.group(2))
            self.routes_by_device[device_port] = host_port
            return f"device {device_port} in host {host_port}"

        query_match = _UKM_QUERY_PATTERN.fullmatch(command)
        if query_match is not None:
            device_port = int(query_match.group(1))
            host_port = self.routes_by_device[device_port]
            return f"device {device_port} in host {host_port}"

        raise AssertionError(f"Unexpected UKM-404 command {command!r}")


def test_physical_lab_smoke_sequence_applies_expected_routes() -> None:
    config = load_config(Path("examples/physical-local.yaml"))
    graph = build_resource_graph(config)
    uhd_transport = ScriptedUhd808Transport()
    ukm_a_transport = ScriptedUkm404Transport()
    ukm_b_transport = ScriptedUkm404Transport()
    drivers: dict[str, Driver] = {
        "video_matrix_uhd808": OreiUhd808VideoDriver(
            "video_matrix_uhd808",
            transport=uhd_transport,
        ),
        "usb_matrix_ukm404_a": OreiUkm404UsbDriver(
            "usb_matrix_ukm404_a",
            transport=ukm_a_transport,
        ),
        "usb_matrix_ukm404_b": OreiUkm404UsbDriver(
            "usb_matrix_ukm404_b",
            transport=ukm_b_transport,
        ),
    }

    desktop = _apply_workspace(graph, drivers, "desktop")
    assert desktop.observed_state == {
        "video_matrix_uhd808": {
            "connected": True,
            "state_status": "observed",
            "routes": {"1": "1", "2": "2"},
        },
        "usb_matrix_ukm404_a": {
            "connected": True,
            "state_status": "observed",
            "routes": {"1": "1", "2": "1"},
        },
    }

    work = _apply_workspace(graph, drivers, "work")
    assert work.observed_state == {
        "video_matrix_uhd808": {
            "connected": True,
            "state_status": "observed",
            "routes": {"1": "3", "2": "4"},
        },
        "usb_matrix_ukm404_a": {
            "connected": True,
            "state_status": "observed",
            "routes": {"1": "2", "2": "2"},
        },
    }

    hybrid = _apply_workspace(graph, drivers, "hybrid_meeting")
    assert hybrid.observed_state == {
        "video_matrix_uhd808": {
            "connected": True,
            "state_status": "observed",
            "routes": {"1": "1", "2": "3"},
        },
        "usb_matrix_ukm404_a": {
            "connected": True,
            "state_status": "observed",
            "routes": {"1": "1", "2": "1"},
        },
        "usb_matrix_ukm404_b": {
            "connected": True,
            "state_status": "observed",
            "routes": {"1": "2", "2": "2", "3": "2"},
        },
    }

    assert uhd_transport.commands[-4:] == [
        "s in 1 av out 1!",
        "r av out 0!",
        "s in 3 av out 2!",
        "r av out 0!",
    ]
    assert ukm_b_transport.routes_by_device == {1: 2, 2: 2, 3: 2}


def _apply_workspace(graph, drivers: dict[str, Driver], workspace_id: str):
    plan = plan_workspace(graph, workspace_id, drivers, transaction_id=f"tx_{workspace_id}")
    assert plan.valid

    result = execute_plan(plan, drivers)

    assert result.status is TransactionResultStatus.SUCCESS
    return result
