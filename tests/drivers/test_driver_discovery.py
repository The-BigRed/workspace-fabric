from __future__ import annotations

import pytest

from workspace_fabric.config.models import DriverConfig
from workspace_fabric.drivers import (
    ApiCompatibilityVersion,
    DriverIssueCategory,
    DuplicateDriverTypeError,
    IncompatibleDriverApiError,
    MissingDriverError,
    PluginDescriptor,
    create_driver,
    discover_drivers,
    get_driver_types,
)


def _factory(config):
    return object()


def _descriptor(driver_type: str, *, supported_api: str | ApiCompatibilityVersion = "1.0"):
    return PluginDescriptor(
        driver_type=driver_type,
        display_name=driver_type.replace("_", " ").title(),
        driver_version="1.0.0",
        supported_driver_api=supported_api,
        factory=_factory,
    )


class FakeEntryPoint:
    def __init__(
        self,
        name: str,
        loaded=None,
        *,
        value: str | None = None,
        error: Exception | None = None,
    ) -> None:
        self.name = name
        self.value = value or f"tests:{name}"
        self._loaded = loaded
        self._error = error

    def load(self):
        if self._error is not None:
            raise self._error
        return self._loaded


class FakeEntryPoints(tuple):
    def select(self, *, group: str):
        assert group == "workspace_fabric.drivers"
        return self


def test_entry_point_discovery_loads_compatible_plugin_descriptors() -> None:
    result = discover_drivers(
        [
            FakeEntryPoint("z_driver", _descriptor("z_driver")),
            FakeEntryPoint("a_driver", lambda: _descriptor("a_driver")),
        ]
    )

    assert tuple(result.drivers) == ("a_driver", "z_driver")
    assert result.issues == ()


def test_entry_point_discovery_reflects_installed_entry_point_set() -> None:
    installed = discover_drivers([FakeEntryPoint("test_driver", _descriptor("test_driver"))])
    uninstalled = discover_drivers([])

    assert installed.available_types == ("test_driver",)
    assert uninstalled.available_types == ()


def test_duplicate_driver_type_is_reported_and_excluded() -> None:
    result = discover_drivers(
        [
            FakeEntryPoint("first", _descriptor("duplicate_driver")),
            FakeEntryPoint("second", _descriptor("duplicate_driver")),
        ]
    )

    assert "duplicate_driver" not in result.drivers
    assert result.issues[0].issue.category == DriverIssueCategory.DUPLICATE_DRIVER_TYPE.value
    assert result.issues[0].driver_type == "duplicate_driver"


def test_create_driver_rejects_duplicate_driver_type(monkeypatch) -> None:
    from workspace_fabric.drivers import factory

    monkeypatch.setattr(
        factory.metadata,
        "entry_points",
        lambda: FakeEntryPoints(
            (
                FakeEntryPoint("first", _descriptor("duplicate_driver")),
                FakeEntryPoint("second", _descriptor("duplicate_driver")),
            )
        ),
    )

    with pytest.raises(DuplicateDriverTypeError) as exc_info:
        create_driver(
            DriverConfig(
                id="duplicate",
                type="duplicate_driver",
                fabric="local",
            )
        )

    assert exc_info.value.issue.category == DriverIssueCategory.DUPLICATE_DRIVER_TYPE.value


def test_plugin_load_failure_is_isolated_and_reported() -> None:
    result = discover_drivers(
        [
            FakeEntryPoint("broken", error=RuntimeError("boom")),
            FakeEntryPoint("working", _descriptor("working")),
        ]
    )

    assert result.available_types == ("working",)
    assert len(result.issues) == 1
    assert result.issues[0].issue.category == DriverIssueCategory.PLUGIN_LOAD_FAILED.value
    assert result.issues[0].exception_type == "RuntimeError"


def test_create_driver_reports_missing_driver_with_available_types(monkeypatch) -> None:
    from workspace_fabric.drivers import factory

    monkeypatch.setattr(
        factory.metadata,
        "entry_points",
        lambda: FakeEntryPoints((FakeEntryPoint("working", _descriptor("working")),)),
    )

    with pytest.raises(MissingDriverError) as exc_info:
        create_driver(
            DriverConfig(
                id="missing",
                type="missing_driver",
                fabric="local",
            )
        )

    assert exc_info.value.issue.category == DriverIssueCategory.MISSING_DRIVER.value
    assert exc_info.value.available_types == ("working",)
    assert "pip install workspace-fabric-driver-missing-driver" in str(exc_info.value)


def test_incompatible_driver_is_reported_and_rejected(monkeypatch) -> None:
    from workspace_fabric.drivers import factory

    monkeypatch.setattr(
        factory.metadata,
        "entry_points",
        lambda: FakeEntryPoints(
            (
                FakeEntryPoint(
                    "future_driver",
                    _descriptor("future_driver", supported_api=ApiCompatibilityVersion(2, 0)),
                ),
            )
        ),
    )

    result = discover_drivers(
        factory.metadata.entry_points().select(group="workspace_fabric.drivers")
    )

    assert result.available_types == ()
    assert result.issues[0].issue.category == DriverIssueCategory.INCOMPATIBLE_DRIVER_API.value
    with pytest.raises(IncompatibleDriverApiError):
        create_driver(
            DriverConfig(
                id="future",
                type="future_driver",
                fabric="local",
            )
        )


def test_get_driver_types_uses_entry_point_metadata(monkeypatch) -> None:
    from workspace_fabric.drivers import factory

    monkeypatch.setattr(
        factory.metadata,
        "entry_points",
        lambda: FakeEntryPoints(
            (
                FakeEntryPoint("b_driver", _descriptor("b_driver")),
                FakeEntryPoint("a_driver", _descriptor("a_driver")),
            )
        ),
    )

    assert get_driver_types() == ("a_driver", "b_driver")
