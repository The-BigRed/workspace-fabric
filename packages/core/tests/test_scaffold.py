"""Tests for the core package scaffold.

Validates that the Phase 4.2 scaffold builds, installs, and does not expose
incomplete or broken entry points.
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
    """Verify that core scaffold does not declare incomplete console scripts."""
    core_dir = Path(__file__).parent.parent
    pyproject_path = core_dir / "pyproject.toml"

    content = pyproject_path.read_text()
    message = "Core scaffold should not declare entry points; CLI will be added in Phase 4.3"
    assert "[project.scripts]" not in content, message


def test_core_package_can_be_imported():
    """Verify that the core package can be imported."""
    import workspace_fabric  # noqa: F401


def test_core_package_installs_in_isolated_venv():
    """Verify core package installs correctly in an isolated environment.

    This test:
    1. Creates a temporary wheel output directory
    2. Creates a temporary virtual environment
    3. Builds the driver-api wheel (local monorepo package)
    4. Builds the core wheel (local monorepo package)
    5. Installs PyYAML into that environment
    6. Installs driver-api wheel into that environment
    7. Installs core wheel into that environment
    8. Verifies core package imports correctly
    9. Verifies no workspace-fabric console script is exposed
    10. Verifies repository dist directories were not modified
    11. Cleans up without modifying the active environment
    """
    monorepo_root = Path(__file__).parent.parent.parent.parent
    driver_api_dir = monorepo_root / "packages" / "driver-api"
    core_dir = monorepo_root / "packages" / "core"
    repo_dist_snapshots = {
        driver_api_dir / "dist": _snapshot_directory(driver_api_dir / "dist"),
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

        # Build driver-api wheel
        build_result = subprocess.run(
            [
                str(python_exe),
                "-m",
                "pip",
                "wheel",
                str(driver_api_dir),
                "--wheel-dir",
                str(wheel_dir),
                "--no-deps",
            ],
            capture_output=True,
            text=True,
        )
        assert (
            build_result.returncode == 0
        ), f"Failed to build driver-api wheel:\n{build_result.stderr}"
        driver_api_wheel = _select_wheel(wheel_dir, "workspace_fabric_driver_api-*.whl")

        # Build core wheel
        build_result = subprocess.run(
            [
                str(python_exe),
                "-m",
                "pip",
                "wheel",
                str(core_dir),
                "--wheel-dir",
                str(wheel_dir),
                "--no-deps",
            ],
            capture_output=True,
            text=True,
        )
        assert build_result.returncode == 0, f"Failed to build core wheel:\n{build_result.stderr}"
        core_wheel = _select_wheel(wheel_dir, "workspace_fabric_core-*.whl")

        # Install PyYAML dependency (driver-api depends on it)
        install_result = subprocess.run(
            [str(python_exe), "-m", "pip", "install", "PyYAML>=6.0.3"],
            capture_output=True,
            text=True,
        )
        assert install_result.returncode == 0, f"Failed to install PyYAML:\n{install_result.stderr}"

        # Install driver-api wheel into venv
        install_result = subprocess.run(
            [str(python_exe), "-m", "pip", "install", "--no-index", str(driver_api_wheel)],
            capture_output=True,
            text=True,
        )
        assert (
            install_result.returncode == 0
        ), f"Failed to install driver-api wheel in venv:\n{install_result.stderr}"

        # Install core wheel into venv
        install_result = subprocess.run(
            [str(python_exe), "-m", "pip", "install", "--no-index", str(core_wheel)],
            capture_output=True,
            text=True,
        )
        assert (
            install_result.returncode == 0
        ), f"Failed to install core wheel in venv:\n{install_result.stderr}"

        # Test import in venv
        import_result = subprocess.run(
            [str(python_exe), "-c", "import workspace_fabric; print('OK')"],
            capture_output=True,
            text=True,
        )
        assert (
            import_result.returncode == 0
        ), f"Failed to import workspace_fabric in venv:\n{import_result.stderr}"
        assert "OK" in import_result.stdout

        # Verify no workspace-fabric console script in venv
        assert not script_path.exists(), (
            f"Core scaffold should not provide workspace-fabric console script, "
            f"but found: {script_path}"
        )

    assert repo_dist_snapshots == {
        path: _snapshot_directory(path) for path in repo_dist_snapshots
    }, "Repository dist directories should not be created, deleted, or modified"
