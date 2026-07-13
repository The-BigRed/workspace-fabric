from __future__ import annotations

import json
from io import StringIO
from pathlib import Path
from typing import Any

import pytest

from workspace_fabric.cli import WorkspaceFabricCLI
from workspace_fabric.config.models import DriverConfig
from workspace_fabric.drivers import (
    ApiCompatibilityVersion,
    DriverConfigurationError,
    DriverIssueCategory,
    PluginDescriptor,
    create_drivers,
    discover_drivers,
    validate_configured_driver_types,
)


class FakeDriver:
    def __init__(self, driver_id: str) -> None:
        self.id = driver_id


def _factory(config: DriverConfig) -> FakeDriver:
    return FakeDriver(config.id)


def _descriptor(
    driver_type: str,
    *,
    driver_version: str = "1.0.0",
    supported_api: str | ApiCompatibilityVersion = "1.0",
    factory=_factory,
) -> PluginDescriptor:
    return PluginDescriptor(
        driver_type=driver_type,
        display_name=driver_type.replace("_", " ").title(),
        driver_version=driver_version,
        supported_driver_api=supported_api,
        factory=factory,
        package_name=f"workspace-fabric-driver-{driver_type.replace('_', '-')}",
    )


def _config(driver_type: str, *, driver_id: str = "configured") -> DriverConfig:
    return DriverConfig(id=driver_id, type=driver_type, fabric="local")


class FakeEntryPoint:
    def __init__(
        self,
        name: str,
        loaded: Any = None,
        *,
        value: str | None = None,
        error: Exception | None = None,
    ) -> None:
        self.name = name
        self.value = value or f"tests:{name}"
        self._loaded = loaded
        self._error = error

    def load(self) -> Any:
        if self._error is not None:
            raise self._error
        return self._loaded


class FakeEntryPoints(tuple):
    def select(self, *, group: str) -> FakeEntryPoints:
        assert group == "workspace_fabric.drivers"
        return self


def _run_cli(
    cli: WorkspaceFabricCLI,
    args: list[str],
    *,
    state_file: Path,
) -> tuple[int, dict[str, Any], dict[str, Any]]:
    stdout = StringIO()
    stderr = StringIO()

    exit_code = cli.run(
        [*args, "--state-file", str(state_file)],
        stdout=stdout,
        stderr=stderr,
    )

    output = json.loads(stdout.getvalue()) if stdout.getvalue() else {}
    error = json.loads(stderr.getvalue()) if stderr.getvalue() else {}
    return exit_code, output, error


def test_installed_driver_is_discovered_and_validates_configured_driver_type() -> None:
    entry_points = [FakeEntryPoint("installed_driver", _descriptor("installed_driver"))]

    discovery = discover_drivers(entry_points)
    validation = validate_configured_driver_types([_config("installed_driver")], entry_points)

    assert discovery.available_types == ("installed_driver",)
    assert validation.valid


def test_removing_unused_driver_does_not_affect_configured_driver_validation() -> None:
    configured = FakeEntryPoint("configured_driver", _descriptor("configured_driver"))
    unused = FakeEntryPoint("unused_driver", _descriptor("unused_driver"))

    with_unused = validate_configured_driver_types(
        [_config("configured_driver")],
        [configured, unused],
    )
    after_unused_removal = validate_configured_driver_types(
        [_config("configured_driver")],
        [configured],
    )

    assert with_unused.valid
    assert after_unused_removal.valid


def test_removing_configured_driver_yields_missing_driver_validation_error() -> None:
    validation = validate_configured_driver_types([_config("removed_driver")], [])

    assert not validation.valid
    assert validation.errors[0].category == DriverIssueCategory.MISSING_DRIVER.value
    assert validation.errors[0].path == "$.drivers.configured.type"
    assert "pip install workspace-fabric-driver-removed-driver" in validation.errors[0].message


def test_config_validate_reports_missing_configured_driver(monkeypatch, tmp_path: Path) -> None:
    from workspace_fabric.drivers import factory

    monkeypatch.setattr(factory.metadata, "entry_points", lambda: FakeEntryPoints(()))
    config_path = tmp_path / "missing-driver.yaml"
    config_path.write_text(
        """
        version: 1
        fabrics:
          local: {}
        drivers:
          configured:
            type: removed_driver
            fabric: local
        """,
        encoding="utf-8",
    )

    exit_code, output, error = _run_cli(
        WorkspaceFabricCLI(),
        ["config", "validate", "--config", str(config_path)],
        state_file=tmp_path / "state.json",
    )

    assert exit_code == 1
    assert output == {}
    assert "missing_driver" in error["error"]["message"]
    assert "$.drivers.configured.type" in error["error"]["message"]


def test_compatible_upgrade_and_rollback_validate_without_core_change() -> None:
    upgraded = [
        FakeEntryPoint(
            "versioned_driver",
            _descriptor("versioned_driver", driver_version="1.1.0"),
        )
    ]
    rolled_back = [
        FakeEntryPoint("versioned_driver", _descriptor("versioned_driver", driver_version="1.0.0"))
    ]

    upgrade_validation = validate_configured_driver_types([_config("versioned_driver")], upgraded)
    rollback_validation = validate_configured_driver_types(
        [_config("versioned_driver")], rolled_back
    )

    assert upgrade_validation.valid
    assert rollback_validation.valid


def test_incompatible_driver_fails_before_controller_construction(monkeypatch) -> None:
    from workspace_fabric.drivers import factory as driver_factory

    constructed: list[str] = []

    def factory(config: DriverConfig) -> FakeDriver:
        constructed.append(config.id)
        return FakeDriver(config.id)

    entry_points = [
        FakeEntryPoint(
            "future_driver",
            _descriptor(
                "future_driver",
                supported_api=ApiCompatibilityVersion(2, 0),
                factory=factory,
            ),
        )
    ]
    monkeypatch.setattr(
        driver_factory.metadata,
        "entry_points",
        lambda: FakeEntryPoints(tuple(entry_points)),
    )

    validation = validate_configured_driver_types([_config("future_driver")], entry_points)

    assert not validation.valid
    assert validation.errors[0].category == DriverIssueCategory.INCOMPATIBLE_DRIVER_API.value
    with pytest.raises(DriverConfigurationError) as exc_info:
        create_drivers([_config("future_driver")])
    assert exc_info.value.issues[0].category == DriverIssueCategory.INCOMPATIBLE_DRIVER_API.value
    assert constructed == []


def test_broken_unused_plugin_does_not_block_configured_compatible_driver() -> None:
    entry_points = [
        FakeEntryPoint("broken_unused", error=RuntimeError("boom")),
        FakeEntryPoint("configured_driver", _descriptor("configured_driver")),
    ]

    discovery = discover_drivers(entry_points)
    validation = validate_configured_driver_types([_config("configured_driver")], entry_points)

    assert discovery.available_types == ("configured_driver",)
    assert discovery.issues[0].issue.category == DriverIssueCategory.PLUGIN_LOAD_FAILED.value
    assert validation.valid


def test_broken_configured_plugin_fails_validation() -> None:
    entry_points = [FakeEntryPoint("broken_driver", error=RuntimeError("boom"))]

    validation = validate_configured_driver_types([_config("broken_driver")], entry_points)

    assert not validation.valid
    assert validation.errors[0].category == DriverIssueCategory.PLUGIN_LOAD_FAILED.value


def test_duplicate_configured_driver_type_fails_validation() -> None:
    entry_points = [
        FakeEntryPoint("first", _descriptor("duplicate_driver")),
        FakeEntryPoint("second", _descriptor("duplicate_driver")),
    ]

    validation = validate_configured_driver_types([_config("duplicate_driver")], entry_points)

    assert not validation.valid
    assert validation.errors[0].category == DriverIssueCategory.DUPLICATE_DRIVER_TYPE.value


def test_unrelated_compatible_driver_continues_loading_when_other_plugins_fail() -> None:
    entry_points = [
        FakeEntryPoint("duplicate_first", _descriptor("duplicate_driver")),
        FakeEntryPoint("duplicate_second", _descriptor("duplicate_driver")),
        FakeEntryPoint(
            "future_driver",
            _descriptor("future_driver", supported_api=ApiCompatibilityVersion(2, 0)),
        ),
        FakeEntryPoint("broken_driver", error=RuntimeError("boom")),
        FakeEntryPoint("configured_driver", _descriptor("configured_driver")),
    ]

    discovery = discover_drivers(entry_points)
    validation = validate_configured_driver_types([_config("configured_driver")], entry_points)

    assert discovery.available_types == ("configured_driver",)
    assert validation.valid
