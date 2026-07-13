# Milestone 4.6 - Driver Migration

**Completion Date:** 2026-07-13
**Status:** Complete
**Milestone:** Phase 4 - Modular Driver Platform

## Overview

Milestone 4.6 completes the implementation migration started by the Phase 4
package split. Mock, UHD-808, and UKM404 driver implementations now live only in
their independently installable driver packages. The core package keeps the
shared catalog, factory, and compatibility surface, but no longer contains the
driver implementation modules.

## Deliverables

- Removed legacy core implementation modules for:
  - `workspace_fabric.drivers.mock`
  - `workspace_fabric.drivers.video.orei_uhd808`
  - `workspace_fabric.drivers.usb.orei_ukm404`
- Preserved the existing driver package implementations:
  - `workspace_fabric_driver_mock`
  - `workspace_fabric_driver_orei_uhd808`
  - `workspace_fabric_driver_orei_ukm404`
- Updated root tests to import implementation classes from driver packages.
- Removed driver package runtime imports of core configuration models.
- Removed driver package test `pythonpath` coupling to `packages/core`.
- Added source-boundary regression coverage for:
  - No legacy implementation modules in core source.
  - No driver implementation package imports from core source.
  - No core configuration or orchestration imports from driver package source.
- Extended core package regression coverage so `workspace-fabric-core` wheels do
  not include the migrated legacy implementation modules.
- Moved the authoritative core source tree to `packages/core/src/workspace_fabric`.
- Added `packages/core/README.md` for portable core package metadata.
- Added a portable sdist-to-wheel regression test for `workspace-fabric-core`.

## Acceptance Criteria

- Core source imports no OREI implementation packages.
- Driver package source imports no core configuration or orchestration modules.
- Existing unit and mocked transport tests pass.
- Existing physical configuration still resolves the same configured driver
  type identifiers:
  - `mock_video_matrix`
  - `mock_usb_matrix`
  - `orei_uhd808`
  - `orei_ukm404`

## Backward Compatibility

- YAML configuration remains unchanged.
- Stable configured driver type identifiers are unchanged.
- Driver package public implementation imports are preserved.
- Core public catalog and factory imports added in earlier milestones remain
  unchanged.
- Physical protocol behavior is not redesigned in this milestone.

## Packaging Note

During validation, ignored build artifacts from an earlier core wheel build
still contained deleted legacy modules under `packages/core/build/lib`. Those
generated artifacts were removed so fresh wheels reflect the migrated source
layout. The core package isolated-wheel test now verifies that
`workspace-fabric-core` includes the catalog package but does not include the
migrated implementation modules.

## Portable Core Sdist Defect Fix

Root cause:

- `packages/core/pyproject.toml` used
  `package-dir = {"" = "../../src"}` and `where = ["../../src"]`.
- That configuration could build a direct wheel from the monorepo checkout, but
  the generated sdist remained dependent on a parent checkout layout.
- When the sdist was extracted into an isolated build directory, `../../src`
  did not exist, so the wheel build failed with
  `error in 'egg_base' option: '../../src' does not exist or is not a directory`.
- The package metadata also referenced `packages/core/README.md`, which did not
  exist.

Packaging design chosen:

- Move the single authoritative `workspace_fabric` core source tree from the
  repository-level `src` directory to `packages/core/src/workspace_fabric`.
- Point `packages/core/pyproject.toml` at package-local `src`.
- Point root development tooling at `packages/core/src` so source-tree tests
  continue to exercise the same authoritative files.
- Add `packages/core/README.md` so readme metadata exists inside the package
  and inside generated sdists.

Why this works from an extracted sdist:

- The sdist now contains `pyproject.toml`, `README.md`, and
  `src/workspace_fabric` in one self-contained package archive.
- Setuptools package discovery no longer resolves any path outside the
  extracted sdist root.
- The wheel built from the sdist includes the real core implementation and the
  generic driver infrastructure only.

Files changed for the defect fix:

- `packages/core/pyproject.toml`
- `pyproject.toml`
- `packages/core/README.md`
- `packages/core/tests/test_scaffold.py`
- `tests/drivers/test_driver_migration.py`
- `packages/core/src/workspace_fabric/**`
- Phase 4.6 status and implementation documentation.

Regression coverage:

- Cleans stale `build`, `dist`, and `*.egg-info` artifacts for the core package.
- Runs `python -m build packages/core`.
- Confirms both sdist and wheel artifacts are produced.
- Confirms build output uses the sdist-to-wheel path.
- Installs the resulting core wheel into a clean temporary virtual environment.
- Imports `workspace_fabric` and `workspace_fabric.drivers`.
- Calls `get_driver_catalog()` with no implementation drivers installed.
- Confirms core-only installation does not install mock, UHD-808, or UKM404
  driver packages.
- Confirms the wheel contains generic driver infrastructure and excludes
  migrated implementation modules.

## Verification

Commands run:

```powershell
.\.venv\Scripts\python.exe -m black packages src tests
.\.venv\Scripts\python.exe -m ruff check packages src tests
.\.venv\Scripts\python.exe -m pytest tests\drivers -v
.\.venv\Scripts\python.exe -m pytest packages\driver-mock\tests -v
.\.venv\Scripts\python.exe -m pytest packages\driver-orei-uhd808\tests -v
.\.venv\Scripts\python.exe -m pytest packages\driver-orei-ukm404\tests -v
.\.venv\Scripts\python.exe -m pytest tests -v
.\.venv\Scripts\python.exe -m pytest packages\core\tests -v
.\.venv\Scripts\python.exe -m pytest -v
.\.venv\Scripts\python.exe -m build .\packages\core
.\.venv\Scripts\python.exe -m pip wheel --no-deps --wheel-dir .tmp\wheelhouse packages\driver-api packages\driver-mock packages\driver-orei-uhd808 packages\driver-orei-ukm404 packages\core
.\.venv\Scripts\python.exe -m venv .tmp\milestone-4.6-venv
.\.tmp\milestone-4.6-venv\Scripts\python.exe -m pip install PyYAML>=6.0.3 pyserial>=3.5
.\.tmp\milestone-4.6-venv\Scripts\python.exe -m pip install --no-index .tmp\wheelhouse\workspace_fabric_driver_api-1.0.0-py3-none-any.whl .tmp\wheelhouse\workspace_fabric_core-0.3.0-py3-none-any.whl .tmp\wheelhouse\workspace_fabric_driver_mock-1.0.0-py3-none-any.whl .tmp\wheelhouse\workspace_fabric_driver_orei_uhd808-1.0.0-py3-none-any.whl .tmp\wheelhouse\workspace_fabric_driver_orei_ukm404-1.0.0-py3-none-any.whl
.\.tmp\milestone-4.6-venv\Scripts\python.exe -c "from workspace_fabric.drivers import get_driver_catalog; catalog = get_driver_catalog(); expected = {'mock_video_matrix', 'mock_usb_matrix', 'orei_uhd808', 'orei_ukm404'}; available = set(catalog.available_types); missing = expected - available; assert not missing, (missing, catalog.dump()); print(','.join(sorted(available)))"
.\.tmp\milestone-4.6-venv\Scripts\python.exe -m pip show -f workspace-fabric-core
git diff --check
```

Results:

- Black: passed; 75 files left unchanged after formatting the expanded core
  packaging test.
- Ruff: passed; all checks passed.
- Root driver suite: passed, 74 tests.
- Mock driver package tests: passed, 1 test.
- OREI UHD-808 package tests: passed, 1 test.
- OREI UKM404 package tests: passed, 1 test.
- Root test suite: passed, 128 tests.
- Core package tests: passed, 4 tests.
- Full repository suite: passed, 128 tests.
- Core package build: passed through the normal sdist-to-wheel build flow;
  generated `workspace_fabric_core-0.3.0.tar.gz` and
  `workspace_fabric_core-0.3.0-py3-none-any.whl`.
- Wheel build: passed for `packages/driver-api`, `packages/driver-mock`,
  `packages/driver-orei-uhd808`, `packages/driver-orei-ukm404`, and
  `packages/core`.
- Temporary installed-wheel catalog validation passed and reported
  `mock_usb_matrix,mock_video_matrix,orei_uhd808,orei_ukm404`.
- `pip show -f workspace-fabric-core` listed the core driver catalog package
  files and did not list the migrated legacy implementation modules.
- Final core wheel inspection listed only:
  `workspace_fabric/drivers/__init__.py`,
  `workspace_fabric/drivers/catalog.py`,
  `workspace_fabric/drivers/factory.py`,
  `workspace_fabric/drivers/base/__init__.py`,
  `workspace_fabric/drivers/base/types.py`, and
  `workspace_fabric/drivers/remote_console/__init__.py`.
- `git diff --check`: passed with only Git LF-to-CRLF working-copy warnings.

## Deferred Work

- Driver lifecycle upgrade, rollback, uninstall, configured missing-driver, and
  incompatible-plugin deployment scenarios remain Milestone 4.7 work.
- Full physical regression against independently installed OREI packages remains
  Milestone 4.8 work.
