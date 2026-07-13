# Milestone 4.7 - Lifecycle and Compatibility

**Completion Date:** 2026-07-13
**Status:** Complete
**Milestone:** Phase 4 - Modular Driver Platform

## Overview

Milestone 4.7 validates the driver plugin lifecycle behavior required by
ADR-0006. The core now validates configured driver types against installed
entry-point discovery before constructing driver controllers, while preserving
isolation for unrelated broken, incompatible, duplicate, removed, or unused
plugins.

## Deliverables

- Added configured-driver lifecycle validation:
  - `validate_configured_driver_types()`
  - `validate_driver_configuration()`
  - `DriverConfigurationError`
- Wired `workspace-fabric config validate` through configured-driver lifecycle
  validation.
- Updated batch `create_drivers()` to validate all configured driver types
  before constructing any controller instances.
- Added lifecycle tests for:
  - Installed compatible driver
  - Unused installed driver removal
  - Configured driver removal
  - Compatible upgrade
  - Compatible rollback
  - Incompatible Driver API
  - Broken unused plugin
  - Broken configured plugin
  - Duplicate driver type
  - Unrelated compatible driver loading while other plugins fail

## Acceptance Criteria

- Removing an unused driver does not affect validation or startup.
- Removing a configured driver yields a structured `missing_driver` diagnostic
  during validation.
- Compatible upgrades and rollbacks require no core code change.
- Incompatible plugins fail before controller construction.
- Broken configured plugins fail before controller construction.
- Duplicate configured driver types fail before controller construction.
- Unrelated compatible drivers continue loading when practical.

## Backward Compatibility

- Existing YAML configuration remains unchanged.
- Stable configured driver type identifiers remain unchanged:
  - `mock_video_matrix`
  - `mock_usb_matrix`
  - `orei_uhd808`
  - `orei_ukm404`
- Existing single-driver factory behavior remains available through
  `create_driver()`.
- Driver construction remains based on installed package entry points.
- The core still does not import mock or OREI implementation packages.

## Implementation Notes

Configured-driver validation reuses the existing discovery diagnostics from
Milestones 4.4 and 4.5. Validation checks configured `DriverConfig.type` values
against the discovered compatible descriptor set and maps related discovery
issues to configuration paths such as `$.drivers.video_matrix.type`.

Batch construction through `create_drivers()` now validates every configured
driver first. This prevents partial controller construction when a later
configured driver is missing, incompatible, duplicated, or broken.

## Deferred Work

- Milestone 4.8 physical regression remains deferred. This milestone does not
  run hardware smoke tests or add new physical capabilities.

## Verification

Commands run during implementation:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\drivers\test_driver_lifecycle.py -v
.\.venv\Scripts\python.exe -m pytest tests\drivers -v
.\.venv\Scripts\python.exe -m black packages src tests
.\.venv\Scripts\python.exe -m ruff check packages src tests
.\.venv\Scripts\python.exe -m pytest -v
.\.venv\Scripts\python.exe -m pytest packages\core\tests -v
.\.venv\Scripts\python.exe -m build .\packages\core
git diff --check
```

Results:

- Lifecycle test suite: passed, 10 tests.
- Driver test suite: passed, 84 tests.
- Black: passed after formatting the new lifecycle tests.
- Ruff: passed.
- Full repository suite: passed, 138 tests.
- Core package tests: passed, 4 tests.
- Core package build: passed and produced both sdist and wheel through the
  normal sdist-to-wheel flow.
- Final core wheel inspection listed only generic driver infrastructure under
  `workspace_fabric/drivers`: `__init__.py`, `catalog.py`, `factory.py`,
  `base/__init__.py`, `base/types.py`, and `remote_console/__init__.py`.
- `git diff --check`: passed with only Git LF-to-CRLF working-copy warnings.
