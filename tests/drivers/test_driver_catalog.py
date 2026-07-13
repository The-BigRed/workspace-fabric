from __future__ import annotations

from workspace_fabric.drivers import (
    ApiCompatibilityVersion,
    DriverIssueCategory,
    PluginDescriptor,
    build_driver_catalog,
    get_driver_catalog,
)


def _factory(config):
    return object()


def _descriptor(
    driver_type: str,
    *,
    supported_api: str | ApiCompatibilityVersion = "1.0",
) -> PluginDescriptor:
    return PluginDescriptor(
        driver_type=driver_type,
        display_name=driver_type.replace("_", " ").title(),
        driver_version="1.0.0",
        supported_driver_api=supported_api,
        factory=_factory,
        configuration_schema={"connection": {"required": ("host",)}},
        port_metadata={"inputs": {"count": 2, "kind": "test"}},
        capability_metadata={"test_capability": "supported"},
        package_name=f"workspace-fabric-driver-{driver_type.replace('_', '-')}",
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


def test_driver_catalog_lists_available_driver_metadata() -> None:
    catalog = build_driver_catalog([FakeEntryPoint("test_driver", _descriptor("test_driver"))])

    assert catalog.available_types == ("test_driver",)
    assert catalog.unavailable_types == ()

    entry = catalog.drivers["test_driver"]
    assert entry.available is True
    assert entry.display_name == "Test Driver"
    assert entry.driver_version == "1.0.0"
    assert entry.supported_driver_api == "1.0"
    assert entry.configuration_schema["connection"]["required"] == ("host",)
    assert entry.port_metadata["inputs"]["count"] == 2
    assert entry.capability_metadata["test_capability"] == "supported"

    dumped = catalog.dump()
    assert dumped["available_types"] == ["test_driver"]
    assert dumped["drivers"]["test_driver"]["package_name"] == (
        "workspace-fabric-driver-test-driver"
    )


def test_incompatible_driver_is_listed_unavailable_with_metadata_and_diagnostics() -> None:
    catalog = build_driver_catalog(
        [
            FakeEntryPoint(
                "future_driver",
                _descriptor("future_driver", supported_api=ApiCompatibilityVersion(2, 0)),
            )
        ]
    )

    assert catalog.available_types == ()
    assert catalog.unavailable_types == ("future_driver",)

    entry = catalog.drivers["future_driver"]
    assert entry.available is False
    assert entry.display_name == "Future Driver"
    assert entry.supported_driver_api == "2.0"
    assert entry.issues[0].category == DriverIssueCategory.INCOMPATIBLE_DRIVER_API.value
    assert catalog.issues[0].driver_type == "future_driver"


def test_duplicate_driver_type_is_listed_unavailable_with_diagnostics() -> None:
    catalog = build_driver_catalog(
        [
            FakeEntryPoint("first", _descriptor("duplicate_driver")),
            FakeEntryPoint("second", _descriptor("duplicate_driver")),
        ]
    )

    assert catalog.available_types == ()
    assert catalog.unavailable_types == ("duplicate_driver",)

    entry = catalog.drivers["duplicate_driver"]
    assert entry.available is False
    assert entry.display_name is None
    assert entry.issues[0].category == DriverIssueCategory.DUPLICATE_DRIVER_TYPE.value


def test_plugin_load_failure_is_reported_without_blocking_catalog_entries() -> None:
    catalog = build_driver_catalog(
        [
            FakeEntryPoint("broken", error=RuntimeError("boom")),
            FakeEntryPoint("working", _descriptor("working")),
        ]
    )

    assert catalog.available_types == ("working",)
    assert catalog.unavailable_types == ()
    assert catalog.issues[0].category == DriverIssueCategory.PLUGIN_LOAD_FAILED.value
    assert catalog.issues[0].entry_point_name == "broken"
    assert catalog.issues[0].exception_type == "RuntimeError"


def test_installed_driver_catalog_contains_phase_4_metadata() -> None:
    catalog = get_driver_catalog()

    assert "mock_video_matrix" in catalog.available_types
    assert "mock_usb_matrix" in catalog.available_types
    assert "orei_uhd808" in catalog.available_types
    assert "orei_ukm404" in catalog.available_types

    assert catalog.drivers["mock_video_matrix"].port_metadata["inputs"]["dynamic"] is True
    assert catalog.drivers["mock_usb_matrix"].port_metadata["host_ports"]["dynamic"] is True
    assert catalog.drivers["orei_uhd808"].port_metadata["inputs"]["count"] == 8
    assert catalog.drivers["orei_ukm404"].port_metadata["device_ports"]["count"] == 4
