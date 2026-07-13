"""Tests for the core package wheel.

Validates that the core wheel builds from the real Workspace Fabric
implementation and includes the driver catalog package.
"""

import subprocess
import sys
import tarfile
import tempfile
import venv
import zipfile
from pathlib import Path
from shutil import rmtree


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


def _select_file(path: Path, pattern: str) -> Path:
    files = sorted(path.glob(pattern))
    file_names = [file.name for file in files]
    assert len(files) == 1, f"Expected one file matching {pattern}, found: {file_names}"
    return files[0]


def _clean_generated_artifacts(package_dir: Path) -> None:
    """Remove generated package artifacts inside a package directory."""
    package_root = package_dir.resolve()
    candidates = [package_dir / "build", package_dir / "dist"]
    candidates.extend(package_dir.glob("*.egg-info"))

    src_dir = package_dir / "src"
    if src_dir.exists():
        candidates.extend(src_dir.glob("*.egg-info"))

    for candidate in candidates:
        if not candidate.exists():
            continue

        resolved_candidate = candidate.resolve()
        assert resolved_candidate.is_relative_to(package_root), candidate
        if candidate.is_dir():
            rmtree(candidate)
        else:
            candidate.unlink()


def _wheel_names(wheel_path: Path) -> set[str]:
    with zipfile.ZipFile(wheel_path) as wheel_file:
        return {name.replace("\\", "/") for name in wheel_file.namelist()}


def _assert_core_wheel_contains_only_generic_driver_infrastructure(wheel_path: Path) -> None:
    installed_files = _wheel_names(wheel_path)
    expected_files = {
        "workspace_fabric/drivers/__init__.py",
        "workspace_fabric/drivers/catalog.py",
        "workspace_fabric/drivers/factory.py",
        "workspace_fabric/drivers/base/__init__.py",
        "workspace_fabric/drivers/base/types.py",
        "workspace_fabric/drivers/remote_console/__init__.py",
    }
    assert expected_files <= installed_files

    forbidden_prefixes = (
        "workspace_fabric/drivers/mock/",
        "workspace_fabric/drivers/video/",
        "workspace_fabric/drivers/usb/",
        "workspace_fabric_driver_mock/",
        "workspace_fabric_driver_orei_uhd808/",
        "workspace_fabric_driver_orei_ukm404/",
    )
    for forbidden_prefix in forbidden_prefixes:
        assert not any(
            installed_file.startswith(forbidden_prefix) for installed_file in installed_files
        ), forbidden_prefix


def _venv_python(venv_dir: Path) -> Path:
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


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


def test_core_package_builds_portable_sdist_and_core_only_wheel():
    """Verify normal PEP 517 sdist-to-wheel builds for the core package."""
    monorepo_root = Path(__file__).parent.parent.parent.parent
    driver_api_dir = monorepo_root / "packages" / "driver-api"
    core_dir = monorepo_root / "packages" / "core"
    dist_dir = core_dir / "dist"

    _clean_generated_artifacts(core_dir)
    try:
        build_result = subprocess.run(
            [sys.executable, "-m", "build", str(core_dir)],
            cwd=monorepo_root,
            capture_output=True,
            text=True,
        )
        assert (
            build_result.returncode == 0
        ), f"Failed to build core package:\n{build_result.stdout}\n{build_result.stderr}"
        build_output = f"{build_result.stdout}\n{build_result.stderr}"
        assert "Building sdist" in build_output
        assert "Building wheel from sdist" in build_output

        sdist = _select_file(dist_dir, "workspace_fabric_core-*.tar.gz")
        core_wheel = _select_file(dist_dir, "workspace_fabric_core-*.whl")

        with tarfile.open(sdist, "r:gz") as sdist_file:
            sdist_names = {member.name.replace("\\", "/") for member in sdist_file.getmembers()}
        assert any(
            name.endswith("/src/workspace_fabric/drivers/catalog.py") for name in sdist_names
        )
        assert not any("/src/workspace_fabric/drivers/mock/" in name for name in sdist_names)
        assert not any("/src/workspace_fabric/drivers/video/" in name for name in sdist_names)
        assert not any("/src/workspace_fabric/drivers/usb/" in name for name in sdist_names)

        _assert_core_wheel_contains_only_generic_driver_infrastructure(core_wheel)

        with tempfile.TemporaryDirectory() as tmpdir:
            temp_dir = Path(tmpdir)
            wheelhouse = temp_dir / "wheelhouse"
            wheelhouse.mkdir()

            driver_api_build_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "wheel",
                    str(driver_api_dir),
                    "--wheel-dir",
                    str(wheelhouse),
                    "--no-deps",
                ],
                capture_output=True,
                text=True,
            )
            assert driver_api_build_result.returncode == 0, (
                "Failed to build driver-api wheel:\n"
                f"{driver_api_build_result.stdout}\n{driver_api_build_result.stderr}"
            )

            venv_dir = temp_dir / "test_venv"
            venv.create(venv_dir, with_pip=True)
            python_exe = _venv_python(venv_dir)

            install_dependency_result = subprocess.run(
                [str(python_exe), "-m", "pip", "install", "PyYAML>=6.0.3"],
                capture_output=True,
                text=True,
            )
            assert install_dependency_result.returncode == 0, (
                "Failed to install runtime dependency:\n"
                f"{install_dependency_result.stdout}\n{install_dependency_result.stderr}"
            )

            install_result = subprocess.run(
                [
                    str(python_exe),
                    "-m",
                    "pip",
                    "install",
                    "--no-index",
                    "--find-links",
                    str(wheelhouse),
                    str(core_wheel),
                ],
                capture_output=True,
                text=True,
            )
            assert install_result.returncode == 0, (
                "Failed to install core wheel:\n"
                f"{install_result.stdout}\n{install_result.stderr}"
            )

            import_result = subprocess.run(
                [
                    str(python_exe),
                    "-c",
                    (
                        "import workspace_fabric\n"
                        "import workspace_fabric.drivers\n"
                        "from workspace_fabric.drivers import get_driver_catalog\n"
                        "catalog = get_driver_catalog()\n"
                        "assert catalog.available_types == (), catalog.dump()\n"
                        "print('core-only catalog ok')\n"
                    ),
                ],
                capture_output=True,
                text=True,
            )
            assert import_result.returncode == 0, (
                "Failed to import core-only installed package:\n"
                f"{import_result.stdout}\n{import_result.stderr}"
            )

            list_result = subprocess.run(
                [str(python_exe), "-m", "pip", "list", "--format=freeze"],
                capture_output=True,
                text=True,
            )
            assert (
                list_result.returncode == 0
            ), f"Failed to list installed packages:\n{list_result.stderr}"
            installed_packages = list_result.stdout.lower()
            assert "workspace-fabric-driver-mock" not in installed_packages
            assert "workspace-fabric-driver-orei-uhd808" not in installed_packages
            assert "workspace-fabric-driver-orei-ukm404" not in installed_packages

            show_result = subprocess.run(
                [str(python_exe), "-m", "pip", "show", "-f", "workspace-fabric-core"],
                capture_output=True,
                text=True,
            )
            assert (
                show_result.returncode == 0
            ), f"Failed to inspect workspace-fabric-core files:\n{show_result.stderr}"
            installed_files = show_result.stdout.replace("\\", "/")
            assert "workspace_fabric/drivers/catalog.py" in installed_files
            assert "workspace_fabric/drivers/factory.py" in installed_files
            assert "workspace_fabric/drivers/mock/" not in installed_files
            assert "workspace_fabric/drivers/video/" not in installed_files
            assert "workspace_fabric/drivers/usb/" not in installed_files
    finally:
        _clean_generated_artifacts(core_dir)


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
        assert "workspace_fabric/drivers/mock/base.py" not in installed_files
        assert "workspace_fabric/drivers/video/orei_uhd808.py" not in installed_files
        assert "workspace_fabric/drivers/usb/orei_ukm404.py" not in installed_files

        # Verify no workspace-fabric console script in venv
        assert not script_path.exists(), (
            f"Core scaffold should not provide workspace-fabric console script, "
            f"but found: {script_path}"
        )

    assert repo_dist_snapshots == {
        path: _snapshot_directory(path) for path in repo_dist_snapshots
    }, "Repository dist directories should not be created, deleted, or modified"
