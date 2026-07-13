"""Tests for the core package wheel.

Validates that the core wheel builds from the real Workspace Fabric
implementation and includes the driver catalog package.
"""

import subprocess
import sys
import tempfile
import venv
from pathlib import Path


def _snapshot_directory(path: Path) -> tuple[bool, tuple[tuple[str, int, int], ...]]:
    if not path.exists():
        return (False, ())

    entries = []
    for entry in sorted(path.rglob("*")):
        stat = entry.stat()
        entries.append((entry.relative_to(path).as_posix(), stat.st_mtime_ns, stat.st_size))
    return (True, tuple(entries))


def _select_wheel(wheel_dir: Path, pattern: str) -> Path:
    wheels = sorted(wheel_dir.glob(pattern))
    wheel_names = [wheel.name for wheel in wheels]
    assert len(wheels) == 1, f"Expected one wheel matching {pattern}, found: {wheel_names}"
    return wheels[0]


def test_core_package_scaffold_has_no_entry_points():
    """Verify that core package does not declare console scripts yet."""
    core_dir = Path(__file__).parent.parent
    pyproject_path = core_dir / "pyproject.toml"

    content = pyproject_path.read_text()
    message = "Core package should not declare console scripts until the package CLI is ready"
    assert "[project.scripts]" not in content, message


def test_core_package_can_be_imported():
    """Verify that the core package can be imported."""
    import workspace_fabric  # noqa: F401


def test_core_package_installs_real_driver_catalog_in_isolated_venv():
    """Verify core and driver wheels expose the installed driver catalog.

    This test:
    1. Creates a temporary wheel output directory
    2. Creates a temporary virtual environment
    3. Builds the core and driver wheels from local monorepo packages
    4. Installs runtime third-party dependencies into that environment
    5. Installs local wheels into that environment without editable installs
    6. Imports workspace_fabric.drivers from the installed core wheel
    7. Verifies the installed driver entry points populate the catalog
    8. Verifies pip show -f lists the packaged drivers module files
    9. Verifies no workspace-fabric console script is exposed
    10. Verifies repository dist directories were not modified
    11. Cleans up without modifying the active environment
    """
    monorepo_root = Path(__file__).parent.parent.parent.parent
    driver_api_dir = monorepo_root / "packages" / "driver-api"
    driver_mock_dir = monorepo_root / "packages" / "driver-mock"
    driver_orei_uhd808_dir = monorepo_root / "packages" / "driver-orei-uhd808"
    driver_orei_ukm404_dir = monorepo_root / "packages" / "driver-orei-ukm404"
    core_dir = monorepo_root / "packages" / "core"
    repo_dist_snapshots = {
        driver_api_dir / "dist": _snapshot_directory(driver_api_dir / "dist"),
        driver_mock_dir / "dist": _snapshot_directory(driver_mock_dir / "dist"),
        driver_orei_uhd808_dir / "dist": _snapshot_directory(driver_orei_uhd808_dir / "dist"),
        driver_orei_ukm404_dir / "dist": _snapshot_directory(driver_orei_ukm404_dir / "dist"),
        core_dir / "dist": _snapshot_directory(core_dir / "dist"),
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        temp_dir = Path(tmpdir)
        wheel_dir = temp_dir / "wheelhouse"
        wheel_dir.mkdir()

        # Create temporary virtual environment
        venv_dir = temp_dir / "test_venv"
        venv.create(venv_dir, with_pip=True)

        # Determine the Python executable in the venv
        if sys.platform == "win32":
            python_exe = venv_dir / "Scripts" / "python.exe"
            script_path = venv_dir / "Scripts" / "workspace-fabric.exe"
        else:
            python_exe = venv_dir / "bin" / "python"
            script_path = venv_dir / "bin" / "workspace-fabric"

        package_dirs = (
            driver_api_dir,
            driver_mock_dir,
            driver_orei_uhd808_dir,
            driver_orei_ukm404_dir,
            core_dir,
        )
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
            assert (
                build_result.returncode == 0
            ), f"Failed to build wheel for {package_dir}:\n{build_result.stderr}"

        driver_api_wheel = _select_wheel(wheel_dir, "workspace_fabric_driver_api-*.whl")
        driver_mock_wheel = _select_wheel(wheel_dir, "workspace_fabric_driver_mock-*.whl")
        driver_orei_uhd808_wheel = _select_wheel(
            wheel_dir, "workspace_fabric_driver_orei_uhd808-*.whl"
        )
        driver_orei_ukm404_wheel = _select_wheel(
            wheel_dir, "workspace_fabric_driver_orei_ukm404-*.whl"
        )
        core_wheel = _select_wheel(wheel_dir, "workspace_fabric_core-*.whl")

        # Install third-party runtime dependencies before local --no-index wheels.
        install_result = subprocess.run(
            [str(python_exe), "-m", "pip", "install", "PyYAML>=6.0.3", "pyserial>=3.5"],
            capture_output=True,
            text=True,
        )
        assert (
            install_result.returncode == 0
        ), f"Failed to install runtime dependencies:\n{install_result.stderr}"

        install_result = subprocess.run(
            [
                str(python_exe),
                "-m",
                "pip",
                "install",
                "--no-index",
                str(driver_api_wheel),
                str(core_wheel),
                str(driver_mock_wheel),
                str(driver_orei_uhd808_wheel),
                str(driver_orei_ukm404_wheel),
            ],
            capture_output=True,
            text=True,
        )
        assert (
            install_result.returncode == 0
        ), f"Failed to install local wheels in venv:\n{install_result.stderr}"

        # Test import in venv
        import_result = subprocess.run(
            [
                str(python_exe),
                "-c",
                (
                    "from workspace_fabric.drivers import get_driver_catalog\n"
                    "catalog = get_driver_catalog()\n"
                    "expected = {"
                    "'mock_video_matrix', 'mock_usb_matrix', "
                    "'orei_uhd808', 'orei_ukm404'"
                    "}\n"
                    "available = set(catalog.available_types)\n"
                    "missing = expected - available\n"
                    "assert not missing, (missing, catalog.dump())\n"
                    "print(','.join(sorted(available)))\n"
                ),
            ],
            capture_output=True,
            text=True,
        )
        assert (
            import_result.returncode == 0
        ), f"Failed to import installed driver catalog:\n{import_result.stderr}"
        assert "mock_video_matrix" in import_result.stdout
        assert "orei_ukm404" in import_result.stdout

        show_result = subprocess.run(
            [str(python_exe), "-m", "pip", "show", "-f", "workspace-fabric-core"],
            capture_output=True,
            text=True,
        )
        assert (
            show_result.returncode == 0
        ), f"Failed to inspect workspace-fabric-core files:\n{show_result.stderr}"
        installed_files = show_result.stdout.replace("\\", "/")
        assert "workspace_fabric/drivers/__init__.py" in installed_files
        assert "workspace_fabric/drivers/catalog.py" in installed_files
        assert "workspace_fabric/drivers/factory.py" in installed_files
        assert "workspace_fabric/drivers/base/__init__.py" in installed_files
        assert "workspace_fabric/drivers/base/types.py" in installed_files

        # Verify no workspace-fabric console script in venv
        assert not script_path.exists(), (
            f"Core scaffold should not provide workspace-fabric console script, "
            f"but found: {script_path}"
        )

    assert repo_dist_snapshots == {
        path: _snapshot_directory(path) for path in repo_dist_snapshots
    }, "Repository dist directories should not be created, deleted, or modified"
