from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

from workspace_fabric.drivers.base import ApiCompatibilityVersion, PluginDescriptor
from workspace_fabric.drivers.factory import (
    CORE_DRIVER_API_VERSION,
    DriverDiscoveryIssue,
    discover_drivers,
)


@dataclass(frozen=True, slots=True)
class DriverCatalogIssue:
    category: str
    message: str
    path: str | None = None
    entry_point_name: str | None = None
    entry_point_value: str | None = None
    driver_type: str | None = None
    exception_type: str | None = None
    exception_message: str | None = None

    @classmethod
    def from_discovery_issue(cls, issue: DriverDiscoveryIssue) -> DriverCatalogIssue:
        return cls(
            category=issue.issue.category,
            message=issue.issue.message,
            path=issue.issue.path,
            entry_point_name=issue.entry_point_name,
            entry_point_value=issue.entry_point_value,
            driver_type=issue.driver_type,
            exception_type=issue.exception_type,
            exception_message=issue.exception_message,
        )

    def dump(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "category": self.category,
            "message": self.message,
        }
        optional_fields = {
            "path": self.path,
            "entry_point_name": self.entry_point_name,
            "entry_point_value": self.entry_point_value,
            "driver_type": self.driver_type,
            "exception_type": self.exception_type,
            "exception_message": self.exception_message,
        }
        data.update({key: value for key, value in optional_fields.items() if value is not None})
        return data


@dataclass(frozen=True, slots=True)
class DriverCatalogEntry:
    driver_type: str
    display_name: str | None
    driver_version: str | None
    supported_driver_api: str | None
    available: bool
    package_name: str | None = None
    is_mock: bool = False
    configuration_schema: Mapping[str, Any] = field(default_factory=dict)
    port_metadata: Mapping[str, Any] = field(default_factory=dict)
    capability_metadata: Mapping[str, Any] = field(default_factory=dict)
    issues: tuple[DriverCatalogIssue, ...] = ()

    @classmethod
    def from_descriptor(
        cls,
        descriptor: PluginDescriptor,
        *,
        available: bool,
        issues: Iterable[DriverCatalogIssue] = (),
    ) -> DriverCatalogEntry:
        return cls(
            driver_type=descriptor.driver_type,
            display_name=descriptor.display_name,
            driver_version=descriptor.driver_version,
            supported_driver_api=str(descriptor.supported_driver_api),
            available=available,
            package_name=descriptor.package_name,
            is_mock=descriptor.is_mock,
            configuration_schema=dict(descriptor.configuration_schema),
            port_metadata=dict(descriptor.port_metadata),
            capability_metadata=dict(descriptor.capability_metadata),
            issues=tuple(issues),
        )

    @classmethod
    def unavailable(
        cls,
        *,
        driver_type: str,
        issues: Iterable[DriverCatalogIssue],
    ) -> DriverCatalogEntry:
        return cls(
            driver_type=driver_type,
            display_name=None,
            driver_version=None,
            supported_driver_api=None,
            available=False,
            issues=tuple(issues),
        )

    def dump(self) -> dict[str, Any]:
        return {
            "driver_type": self.driver_type,
            "display_name": self.display_name,
            "driver_version": self.driver_version,
            "supported_driver_api": self.supported_driver_api,
            "available": self.available,
            "package_name": self.package_name,
            "is_mock": self.is_mock,
            "configuration_schema": dict(self.configuration_schema),
            "port_metadata": dict(self.port_metadata),
            "capability_metadata": dict(self.capability_metadata),
            "issues": [issue.dump() for issue in self.issues],
        }


@dataclass(frozen=True, slots=True)
class DriverCatalog:
    drivers: Mapping[str, DriverCatalogEntry]
    issues: tuple[DriverCatalogIssue, ...] = ()

    @property
    def available_drivers(self) -> Mapping[str, DriverCatalogEntry]:
        return {
            driver_type: entry for driver_type, entry in self.drivers.items() if entry.available
        }

    @property
    def unavailable_drivers(self) -> Mapping[str, DriverCatalogEntry]:
        return {
            driver_type: entry for driver_type, entry in self.drivers.items() if not entry.available
        }

    @property
    def available_types(self) -> tuple[str, ...]:
        return tuple(sorted(self.available_drivers))

    @property
    def unavailable_types(self) -> tuple[str, ...]:
        return tuple(sorted(self.unavailable_drivers))

    def dump(self) -> dict[str, Any]:
        return {
            "available_types": list(self.available_types),
            "unavailable_types": list(self.unavailable_types),
            "drivers": {
                driver_type: entry.dump() for driver_type, entry in sorted(self.drivers.items())
            },
            "issues": [issue.dump() for issue in self.issues],
        }


def build_driver_catalog(
    entry_points: Iterable[Any] | None = None,
    *,
    accepted_version: ApiCompatibilityVersion = CORE_DRIVER_API_VERSION,
) -> DriverCatalog:
    discovery = discover_drivers(entry_points, accepted_version=accepted_version)
    catalog_issues = tuple(
        DriverCatalogIssue.from_discovery_issue(issue) for issue in discovery.issues
    )
    issues_by_driver_type = _issues_by_driver_type(catalog_issues)

    entries: dict[str, DriverCatalogEntry] = {
        driver_type: DriverCatalogEntry.from_descriptor(
            descriptor,
            available=True,
            issues=issues_by_driver_type.get(driver_type, ()),
        )
        for driver_type, descriptor in discovery.drivers.items()
    }

    for issue in discovery.issues:
        if issue.driver_type is None or issue.driver_type in entries:
            continue

        entry_issues = issues_by_driver_type.get(issue.driver_type, ())
        if issue.descriptor is not None:
            entries[issue.driver_type] = DriverCatalogEntry.from_descriptor(
                issue.descriptor,
                available=False,
                issues=entry_issues,
            )
            continue

        entries[issue.driver_type] = DriverCatalogEntry.unavailable(
            driver_type=issue.driver_type,
            issues=entry_issues,
        )

    return DriverCatalog(drivers=dict(sorted(entries.items())), issues=catalog_issues)


def get_driver_catalog() -> DriverCatalog:
    return build_driver_catalog()


def get_available_driver_catalog() -> Mapping[str, DriverCatalogEntry]:
    return get_driver_catalog().available_drivers


def _issues_by_driver_type(
    issues: Iterable[DriverCatalogIssue],
) -> dict[str, tuple[DriverCatalogIssue, ...]]:
    grouped: dict[str, list[DriverCatalogIssue]] = {}
    for issue in issues:
        if issue.driver_type is None:
            continue
        grouped.setdefault(issue.driver_type, []).append(issue)

    return {driver_type: tuple(driver_issues) for driver_type, driver_issues in grouped.items()}
