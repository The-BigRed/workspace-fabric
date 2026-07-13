# Milestone 4.8 - Physical Regression

**Completion Date:** 2026-07-13
**Status:** Complete
**Milestone:** Phase 4 - Modular Driver Platform

## Overview

Milestone 4.8 validates that the Phase 3 physical routing behavior still works
after the OREI drivers have been migrated out of the core package. The
regression path builds and installs independently versioned driver wheels into a
clean temporary virtual environment, then replays the physical-lab route
sequence through the installed packages.

This milestone does not add hardware capabilities or begin Phase 5 work.

## Deliverables

- Added installed-wheel physical regression coverage in
  `tests/physical/test_physical_smoke.py`.
- Built the driver API, UHD-808, UKM404, and core wheels before the isolated
  validation run.
- Installed those wheels into a clean temporary virtual environment.
- Imported `workspace_fabric`, `workspace_fabric.drivers`, and the OREI driver
  packages from the temporary virtual environment.
- Replayed `desktop`, `work`, and `hybrid_meeting` against the physical-lab
  configuration using scripted OREI transports.
- Verified UHD-808 and UKM404 observed route state after each transition.
- Verified structured hardware rejection behavior still produces a
  `hardware_rejected_command` transaction error.
- Inspected the core wheel to confirm it contains generic driver
  infrastructure and does not contain migrated mock, UHD-808, or UKM404
  implementation modules.

## Acceptance Criteria

- `desktop`, `work`, and `hybrid_meeting` pass.
- UHD-808 state remains observed.
- UKM404 state remains observed.
- Structured failure behavior remains intact.
- No vendor-specific imports remain in the core distribution.

## Packaging and Dependency Boundaries

The installed regression environment includes only the core package, the shared
driver API package, and the two OREI implementation packages required for the
physical-lab route sequence. The core wheel is inspected directly to verify that
`workspace_fabric/drivers` contains only generic infrastructure:

- `workspace_fabric/drivers/__init__.py`
- `workspace_fabric/drivers/catalog.py`
- `workspace_fabric/drivers/factory.py`
- `workspace_fabric/drivers/base/__init__.py`
- `workspace_fabric/drivers/base/types.py`
- `workspace_fabric/drivers/remote_console/__init__.py`

The validation asserts that the core wheel does not contain:

- `workspace_fabric/drivers/mock/`
- `workspace_fabric/drivers/video/`
- `workspace_fabric/drivers/usb/`
- `workspace_fabric_driver_mock/`
- `workspace_fabric_driver_orei_uhd808/`
- `workspace_fabric_driver_orei_ukm404/`

It also scans installed core module text for imports of the migrated driver
implementation package names.

## Regression Design

The new installed-wheel test uses the same physical-lab configuration and the
same `desktop`, `work`, and `hybrid_meeting` workspace sequence as the existing
physical smoke test. To keep the test deterministic and safe for automated
validation, it uses scripted UHD-808 and UKM404 transports rather than opening
live serial ports.

The scripted transports preserve the driver command and observation flow: route
commands update simulated device state, and `observe_state()` reads that state
back through each installed OREI driver implementation. A rejecting UHD-808
transport validates that hardware command rejection still maps to the structured
transaction failure category expected by the core.

## Verification

Commands run during implementation:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\physical -v
.\.venv\Scripts\python.exe -m black packages src tests
.\.venv\Scripts\python.exe -m ruff check packages src tests
.\.venv\Scripts\python.exe -m pytest -v
.\.venv\Scripts\python.exe -m pytest packages\core\tests -v
.\.venv\Scripts\python.exe -m build .\packages\core
.\.venv\Scripts\python.exe -c "<inspect packages/core/dist workspace_fabric_core wheel>"
git diff --check
```

Results:

- Targeted physical test suite: passed, 2 tests.
- Black: passed, 76 files left unchanged.
- Ruff: passed.
- Full repository suite: passed, 139 tests.
- Core package tests: passed, 4 tests.
- Core package build: passed and produced both
  `workspace_fabric_core-0.3.0.tar.gz` and
  `workspace_fabric_core-0.3.0-py3-none-any.whl`.
- Final core wheel inspection listed only generic driver infrastructure under
  `workspace_fabric/drivers` and reported no forbidden entries.
- `git diff --check`: passed with Git LF-to-CRLF working-copy warnings.
- Installed-wheel physical regression produced `physical regression ok` inside
  the temporary virtual environment.
