from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import venv
import zipfile
from pathlib import Path
from textwrap import dedent

from workspace_fabric.config import load_config
from workspace_fabric.core.graph import build_resource_graph
from workspace_fabric.core.planner import plan_workspace
from workspace_fabric.core.transactions import TransactionResultStatus, execute_plan
from workspace_fabric.drivers import Driver
from workspace_fabric_driver_orei_uhd808 import OreiUhd808VideoDriver
from workspace_fabric_driver_orei_ukm404 import OreiUkm404UsbDriver

_UHD_ROUTE_PATTERN = re.compile(r"s in (\d+) av out (\d+)!")
_UKM_ROUTE_PATTERN = re.compile(r"set device (\d+) in host (\d+)")
_UKM_QUERY_PATTERN = re.compile(r"get device (\d+) in host")
_INSTALLED_PHYSICAL_REGRESSION_SCRIPT = r"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from workspace_fabric.config import load_config
from workspace_fabric.core.graph import build_resource_graph
from workspace_fabric.core.planner import plan_workspace
from workspace_fabric.core.transactions import TransactionResultStatus, execute_plan
from workspace_fabric.drivers import get_driver_catalog, validate_driver_configuration
from workspace_fabric_driver_orei_uhd808 import OreiUhd808VideoDriver
from workspace_fabric_driver_orei_ukm404 import OreiUkm404UsbDriver

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


class RejectingUhd808Transport:
    def connect(self) -> None:
        pass

    def disconnect(self) -> None:
        pass

    def send_command(self, command: str, *, timeout_seconds: float | None = None) -> str:
        if _UHD_ROUTE_PATTERN.fullmatch(command):
            return "ERROR"
        if command == "r av out 0!":
            return ""
        raise AssertionError(f"Unexpected UHD-808 command {command!r}")


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


def main() -> None:
    config = load_config(Path(sys.argv[1]))
    validate_driver_configuration(config.drivers.values())
    catalog = get_driver_catalog()
    available = set(catalog.available_types)
    assert {"orei_uhd808", "orei_ukm404"} <= available, catalog.dump()
    assert "mock_video_matrix" not in available, catalog.dump()

    graph = build_resource_graph(config)
    uhd_transport = ScriptedUhd808Transport()
    ukm_a_transport = ScriptedUkm404Transport()
    ukm_b_transport = ScriptedUkm404Transport()
    drivers = {
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
    assert desktop.observed_state["video_matrix_uhd808"]["state_status"] == "observed"
    assert desktop.observed_state["usb_matrix_ukm404_a"]["state_status"] == "observed"
    assert desktop.observed_state["video_matrix_uhd808"]["routes"] == {"1": "1", "2": "2"}

    work = _apply_workspace(graph, drivers, "work")
    assert work.observed_state["video_matrix_uhd808"]["state_status"] == "observed"
    assert work.observed_state["usb_matrix_ukm404_a"]["state_status"] == "observed"
    assert work.observed_state["video_matrix_uhd808"]["routes"] == {"1": "3", "2": "4"}

    hybrid = _apply_workspace(graph, drivers, "hybrid_meeting")
    assert hybrid.observed_state["video_matrix_uhd808"] == {
        "connected": True,
        "state_status": "observed",
        "routes": {"1": "1", "2": "3"},
    }
    assert hybrid.observed_state["usb_matrix_ukm404_a"] == {
        "connected": True,
        "state_status": "observed",
        "routes": {"1": "1", "2": "1"},
    }
    assert hybrid.observed_state["usb_matrix_ukm404_b"] == {
        "connected": True,
        "state_status": "observed",
        "routes": {"1": "2", "2": "2", "3": "2"},
    }

    rejecting_driver = OreiUhd808VideoDriver(
        "video_matrix_uhd808",
        transport=RejectingUhd808Transport(),
    )
    failure = rejecting_driver.apply_action(
        rejecting_driver.route_action(input_port=1, output_port=1)
    )
    assert failure.status.value == "failed_apply"
    assert failure.errors[0].category == "hardware_rejected_command"

    print("physical regression ok")


def _apply_workspace(graph, drivers, workspace_id: str):
    plan = plan_workspace(graph, workspace_id, drivers, transaction_id=f"tx_{workspace_id}")
    assert plan.valid

    result = execute_plan(plan, drivers)

    assert result.status is TransactionResultStatus.SUCCESS
    return result


if __name__ == "__main__":
    main()
"""


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


def test_independently_installed_orei_packages_pass_physical_regression() -> None:
    monorepo_root = Path(__file__).parent.parent.parent
    package_dirs = (
        monorepo_root / "packages" / "driver-api",
        monorepo_root / "packages" / "driver-orei-uhd808",
        monorepo_root / "packages" / "driver-orei-ukm404",
        monorepo_root / "packages" / "core",
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        temp_dir = Path(tmpdir)
        wheel_dir = temp_dir / "wheelhouse"
        wheel_dir.mkdir()
        venv_dir = temp_dir / "physical_regression_venv"
        venv.create(venv_dir, with_pip=True)
        python_exe = _venv_python(venv_dir)

        for package_dir in package_dirs:
            build_result = subprocess.run(
                [
                    str(python_exe),
                    "-m",
                    "pip",
                    "wheel",
                    str(package_dir),
                    "--wheel-dir",
                    str(wheel_dir),
                    "--no-deps",
                ],
                capture_output=True,
                text=True,
            )
            assert build_result.returncode == 0, (
                f"Failed to build wheel for {package_dir}:\n"
                f"{build_result.stdout}\n{build_result.stderr}"
            )

        core_wheel = _select_wheel(wheel_dir, "workspace_fabric_core-*.whl")
        _assert_core_wheel_has_no_vendor_driver_implementation(core_wheel)

        install_deps_result = subprocess.run(
            [str(python_exe), "-m", "pip", "install", "PyYAML>=6.0.3", "pyserial>=3.5"],
            capture_output=True,
            text=True,
        )
        assert install_deps_result.returncode == 0, (
            "Failed to install physical regression dependencies:\n"
            f"{install_deps_result.stdout}\n{install_deps_result.stderr}"
        )

        install_result = subprocess.run(
            [
                str(python_exe),
                "-m",
                "pip",
                "install",
                "--no-index",
                str(_select_wheel(wheel_dir, "workspace_fabric_driver_api-*.whl")),
                str(core_wheel),
                str(_select_wheel(wheel_dir, "workspace_fabric_driver_orei_uhd808-*.whl")),
                str(_select_wheel(wheel_dir, "workspace_fabric_driver_orei_ukm404-*.whl")),
            ],
            capture_output=True,
            text=True,
        )
        assert install_result.returncode == 0, (
            "Failed to install physical regression wheels:\n"
            f"{install_result.stdout}\n{install_result.stderr}"
        )

        script_path = temp_dir / "installed_physical_regression.py"
        script_path.write_text(
            dedent(_INSTALLED_PHYSICAL_REGRESSION_SCRIPT),
            encoding="utf-8",
        )
        regression_result = subprocess.run(
            [
                str(python_exe),
                str(script_path),
                str(monorepo_root / "examples" / "physical-local.yaml"),
            ],
            capture_output=True,
            text=True,
        )
        assert regression_result.returncode == 0, (
            "Installed physical regression failed:\n"
            f"{regression_result.stdout}\n{regression_result.stderr}"
        )
        assert "physical regression ok" in regression_result.stdout


def _apply_workspace(graph, drivers: dict[str, Driver], workspace_id: str):
    plan = plan_workspace(graph, workspace_id, drivers, transaction_id=f"tx_{workspace_id}")
    assert plan.valid

    result = execute_plan(plan, drivers)

    assert result.status is TransactionResultStatus.SUCCESS
    return result


def _venv_python(venv_dir: Path) -> Path:
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _select_wheel(wheel_dir: Path, pattern: str) -> Path:
    wheels = sorted(wheel_dir.glob(pattern))
    wheel_names = [wheel.name for wheel in wheels]
    assert len(wheels) == 1, f"Expected one wheel matching {pattern}, found: {wheel_names}"
    return wheels[0]


def _assert_core_wheel_has_no_vendor_driver_implementation(core_wheel: Path) -> None:
    with zipfile.ZipFile(core_wheel) as wheel_file:
        names = {name.replace("\\", "/") for name in wheel_file.namelist()}
        python_sources = {
            name: wheel_file.read(name).decode("utf-8")
            for name in names
            if name.startswith("workspace_fabric/") and name.endswith(".py")
        }

    expected_driver_files = {
        "workspace_fabric/drivers/__init__.py",
        "workspace_fabric/drivers/catalog.py",
        "workspace_fabric/drivers/factory.py",
        "workspace_fabric/drivers/base/__init__.py",
        "workspace_fabric/drivers/base/types.py",
        "workspace_fabric/drivers/remote_console/__init__.py",
    }
    assert expected_driver_files <= names

    forbidden_prefixes = (
        "workspace_fabric/drivers/mock/",
        "workspace_fabric/drivers/video/",
        "workspace_fabric/drivers/usb/",
        "workspace_fabric_driver_mock/",
        "workspace_fabric_driver_orei_uhd808/",
        "workspace_fabric_driver_orei_ukm404/",
    )
    for forbidden_prefix in forbidden_prefixes:
        assert not any(name.startswith(forbidden_prefix) for name in names), forbidden_prefix

    forbidden_imports = (
        "workspace_fabric_driver_mock",
        "workspace_fabric_driver_orei_uhd808",
        "workspace_fabric_driver_orei_ukm404",
    )
    for source_name, source_text in python_sources.items():
        for forbidden_import in forbidden_imports:
            assert forbidden_import not in source_text, source_name
