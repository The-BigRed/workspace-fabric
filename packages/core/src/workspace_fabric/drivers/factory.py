from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from importlib import metadata
from typing import Any

from workspace_fabric.config.models import DriverConfig
from workspace_fabric.drivers.base import (
    DRIVER_API_COMPATIBILITY_VERSION,
    ApiCompatibilityVersion,
    Driver,
    DriverFactory,
    DriverIssue,
    DriverIssueCategory,
    DriverValidationResult,
    PluginDescriptor,
    validate_driver_api_compatibility,
)

ENTRY_POINT_GROUP = "workspace_fabric.drivers"
CORE_DRIVER_API_VERSION = DRIVER_API_COMPATIBILITY_VERSION


@dataclass(frozen=True, slots=True)
class DriverDiscoveryIssue:
    issue: DriverIssue
    entry_point_name: str | None = None
    entry_point_value: str | None = None
    driver_type: str | None = None
    descriptor: PluginDescriptor | None = None
    exception_type: str | None = None
    exception_message: str | None = None


@dataclass(frozen=True, slots=True)
class DriverDiscoveryResult:
    drivers: Mapping[str, PluginDescriptor]
    issues: tuple[DriverDiscoveryIssue, ...] = ()

    @property
    def available_types(self) -> tuple[str, ...]:
        return tuple(sorted(self.drivers))

    def issues_for_driver_type(self, driver_type: str) -> tuple[DriverDiscoveryIssue, ...]:
        return tuple(issue for issue in self.issues if issue.driver_type == driver_type)


class PluginLoadError(ValueError):
    def __init__(
        self,
        *,
        entry_point_name: str,
        entry_point_value: str,
        cause: BaseException,
    ) -> None:
        self.entry_point_name = entry_point_name
        self.entry_point_value = entry_point_value
        self.cause = cause
        self.issue = DriverIssue(
            category=DriverIssueCategory.PLUGIN_LOAD_FAILED.value,
            message=(
                f"Driver plugin entry point {entry_point_name!r} could not be loaded: "
                f"{type(cause).__name__}: {cause}"
            ),
            path=f"entry_points.{ENTRY_POINT_GROUP}.{entry_point_name}",
        )
        super().__init__(self.issue.message)


class MissingDriverError(ValueError):
    def __init__(
        self,
        driver_type: str,
        available_types: Sequence[str],
        discovery_issues: Sequence[DriverDiscoveryIssue] = (),
    ) -> None:
        self.driver_type = driver_type
        self.available_types = tuple(sorted(available_types))
        self.discovery_issues = tuple(discovery_issues)
        self.suggested_install_command = _suggest_install_command(driver_type)
        available = ", ".join(self.available_types) if self.available_types else "none"
        self.issue = DriverIssue(
            category=DriverIssueCategory.MISSING_DRIVER.value,
            message=(
                f"Unsupported driver type {driver_type!r}; available driver types: {available}. "
                f"Suggested install: {self.suggested_install_command}"
            ),
            path=f"$.drivers.{driver_type}",
        )
        super().__init__(self.issue.message)


class DuplicateDriverTypeError(ValueError):
    def __init__(
        self,
        driver_type: str,
        discovery_issues: Sequence[DriverDiscoveryIssue],
    ) -> None:
        self.driver_type = driver_type
        self.discovery_issues = tuple(discovery_issues)
        entry_points = tuple(
            issue.entry_point_name
            for issue in discovery_issues
            if issue.entry_point_name is not None
        )
        self.entry_point_names = entry_points
        listed = ", ".join(entry_points) if entry_points else "unknown"
        self.issue = DriverIssue(
            category=DriverIssueCategory.DUPLICATE_DRIVER_TYPE.value,
            message=(
                f"Duplicate driver type {driver_type!r} was registered by entry points: {listed}"
            ),
            path=f"entry_points.{ENTRY_POINT_GROUP}.{driver_type}",
        )
        super().__init__(self.issue.message)


class IncompatibleDriverApiError(ValueError):
    def __init__(
        self,
        descriptor: PluginDescriptor,
        accepted_version: ApiCompatibilityVersion = CORE_DRIVER_API_VERSION,
        issue: DriverIssue | None = None,
    ) -> None:
        if issue is None:
            validation = validate_driver_api_compatibility(descriptor, accepted_version)
            if validation.valid:
                raise ValueError(
                    f"Driver {descriptor.driver_type!r} is compatible with "
                    f"Driver API {accepted_version}"
                )
            issue = validation.errors[0]
        self.descriptor = descriptor
        self.accepted_version = accepted_version
        self.issue = issue
        super().__init__(issue.message)


class DriverConfigurationError(ValueError):
    def __init__(self, issues: Sequence[DriverIssue]) -> None:
        if not issues:
            raise ValueError("DriverConfigurationError requires at least one issue")

        self.issues = tuple(issues)
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        details = "\n".join(
            f"- [{issue.category}] {issue.path or '$.drivers'}: {issue.message}"
            for issue in self.issues
        )
        return f"Driver configuration validation failed:\n{details}"


class _DiscoveredDriverTypes(Mapping[str, DriverFactory]):
    def __getitem__(self, key: str) -> DriverFactory:
        return get_driver_descriptor(key).factory

    def __iter__(self) -> Iterator[str]:
        return iter(get_driver_types())

    def __len__(self) -> int:
        return len(get_driver_types())


DRIVER_TYPES: Mapping[str, DriverFactory] = _DiscoveredDriverTypes()


def discover_drivers(
    entry_points: Iterable[Any] | None = None,
    *,
    accepted_version: ApiCompatibilityVersion = CORE_DRIVER_API_VERSION,
) -> DriverDiscoveryResult:
    discovered: dict[str, PluginDescriptor] = {}
    source_entry_points: dict[str, tuple[str, ...]] = {}
    duplicate_types: set[str] = set()
    issues: list[DriverDiscoveryIssue] = []

    for entry_point in _sorted_driver_entry_points(entry_points):
        entry_point_name = _entry_point_name(entry_point)
        entry_point_value = _entry_point_value(entry_point)
        try:
            descriptor = _load_plugin_descriptor(entry_point)
        except Exception as exc:
            error = PluginLoadError(
                entry_point_name=entry_point_name,
                entry_point_value=entry_point_value,
                cause=exc,
            )
            issues.append(
                DriverDiscoveryIssue(
                    issue=error.issue,
                    entry_point_name=entry_point_name,
                    entry_point_value=entry_point_value,
                    exception_type=type(exc).__name__,
                    exception_message=str(exc),
                )
            )
            continue

        compatibility = validate_driver_api_compatibility(descriptor, accepted_version)
        if not compatibility.valid:
            issues.append(
                DriverDiscoveryIssue(
                    issue=compatibility.errors[0],
                    entry_point_name=entry_point_name,
                    entry_point_value=entry_point_value,
                    driver_type=descriptor.driver_type,
                    descriptor=descriptor,
                )
            )
            continue

        if descriptor.driver_type in discovered or descriptor.driver_type in duplicate_types:
            previous_entry_points = source_entry_points.get(descriptor.driver_type, ())
            duplicate_entry_points = (*previous_entry_points, entry_point_name)
            discovered.pop(descriptor.driver_type, None)
            source_entry_points[descriptor.driver_type] = duplicate_entry_points
            duplicate_types.add(descriptor.driver_type)
            issues.append(
                _duplicate_driver_type_issue(
                    descriptor.driver_type,
                    duplicate_entry_points,
                    entry_point_name=entry_point_name,
                    entry_point_value=entry_point_value,
                )
            )
            continue

        discovered[descriptor.driver_type] = descriptor
        source_entry_points[descriptor.driver_type] = (entry_point_name,)

    return DriverDiscoveryResult(drivers=dict(sorted(discovered.items())), issues=tuple(issues))


def get_discovered_drivers() -> dict[str, PluginDescriptor]:
    return dict(discover_drivers().drivers)


def get_driver_descriptors() -> dict[str, PluginDescriptor]:
    return get_discovered_drivers()


def get_driver_types() -> tuple[str, ...]:
    return discover_drivers().available_types


def get_driver_descriptor(driver_type: str) -> PluginDescriptor:
    discovery = discover_drivers()
    return _get_driver_descriptor(driver_type, discovery)


def ensure_driver_api_compatible(
    descriptor: PluginDescriptor,
    accepted_version: ApiCompatibilityVersion = CORE_DRIVER_API_VERSION,
) -> None:
    validation = validate_driver_api_compatibility(descriptor, accepted_version)
    if not validation.valid:
        raise IncompatibleDriverApiError(
            descriptor,
            accepted_version,
            validation.errors[0],
        )


def validate_configured_driver_types(
    configs: Iterable[DriverConfig],
    entry_points: Iterable[Any] | None = None,
    *,
    accepted_version: ApiCompatibilityVersion = CORE_DRIVER_API_VERSION,
) -> DriverValidationResult:
    discovery = discover_drivers(entry_points, accepted_version=accepted_version)
    errors = tuple(
        issue
        for issue in (_configured_driver_issue(config, discovery) for config in configs)
        if issue is not None
    )
    return DriverValidationResult(valid=not errors, errors=errors)


def validate_driver_configuration(
    configs: Iterable[DriverConfig],
    entry_points: Iterable[Any] | None = None,
    *,
    accepted_version: ApiCompatibilityVersion = CORE_DRIVER_API_VERSION,
) -> None:
    validation = validate_configured_driver_types(
        configs,
        entry_points,
        accepted_version=accepted_version,
    )
    if not validation.valid:
        raise DriverConfigurationError(validation.errors)


def create_driver(config: DriverConfig) -> Driver:
    discovery = discover_drivers()
    descriptor = _get_driver_descriptor(config.type, discovery)
    return descriptor.factory(config)


def create_drivers(configs: Iterable[DriverConfig]) -> dict[str, Driver]:
    configs = tuple(configs)
    discovery = discover_drivers()
    errors = tuple(
        issue
        for issue in (_configured_driver_issue(config, discovery) for config in configs)
        if issue is not None
    )
    if errors:
        raise DriverConfigurationError(errors)

    return {
        config.id: _get_driver_descriptor(config.type, discovery).factory(config)
        for config in configs
    }


def is_mock_driver_type(driver_type: str) -> bool:
    descriptor = discover_drivers().drivers.get(driver_type)
    return descriptor.is_mock if descriptor is not None else False


def _get_driver_descriptor(
    driver_type: str,
    discovery: DriverDiscoveryResult,
) -> PluginDescriptor:
    descriptor = discovery.drivers.get(driver_type)
    if descriptor is not None:
        return descriptor

    related_issues = discovery.issues_for_driver_type(driver_type)
    incompatible_issue = _first_issue(
        related_issues,
        DriverIssueCategory.INCOMPATIBLE_DRIVER_API.value,
    )
    if incompatible_issue is not None:
        if incompatible_issue.descriptor is not None:
            raise IncompatibleDriverApiError(
                incompatible_issue.descriptor,
                CORE_DRIVER_API_VERSION,
                incompatible_issue.issue,
            )

    duplicate_issues = tuple(
        issue
        for issue in related_issues
        if issue.issue.category == DriverIssueCategory.DUPLICATE_DRIVER_TYPE.value
    )
    if duplicate_issues:
        raise DuplicateDriverTypeError(driver_type, duplicate_issues)

    raise MissingDriverError(driver_type, discovery.available_types, discovery.issues)


def _first_issue(
    issues: Sequence[DriverDiscoveryIssue],
    category: str,
) -> DriverDiscoveryIssue | None:
    for issue in issues:
        if issue.issue.category == category:
            return issue
    return None


def _configured_driver_issue(
    config: DriverConfig,
    discovery: DriverDiscoveryResult,
) -> DriverIssue | None:
    if config.type in discovery.drivers:
        return None

    path = f"$.drivers.{config.id}.type"
    related_issue = _configured_related_issue(config.type, discovery)
    if related_issue is not None:
        return DriverIssue(
            category=related_issue.issue.category,
            message=related_issue.issue.message,
            path=path,
        )

    available = ", ".join(discovery.available_types) if discovery.available_types else "none"
    suggested_install_command = _suggest_install_command(config.type)
    return DriverIssue(
        category=DriverIssueCategory.MISSING_DRIVER.value,
        message=(
            f"Configured driver {config.id!r} uses unavailable driver type {config.type!r}; "
            f"available driver types: {available}. "
            f"Suggested install: {suggested_install_command}"
        ),
        path=path,
    )


def _configured_related_issue(
    driver_type: str,
    discovery: DriverDiscoveryResult,
) -> DriverDiscoveryIssue | None:
    related_issues = discovery.issues_for_driver_type(driver_type)
    for category in (
        DriverIssueCategory.INCOMPATIBLE_DRIVER_API.value,
        DriverIssueCategory.DUPLICATE_DRIVER_TYPE.value,
        DriverIssueCategory.PLUGIN_LOAD_FAILED.value,
    ):
        issue = _first_issue(related_issues, category)
        if issue is not None:
            return issue

    for issue in discovery.issues:
        if (
            issue.issue.category == DriverIssueCategory.PLUGIN_LOAD_FAILED.value
            and issue.driver_type is None
            and issue.entry_point_name == driver_type
        ):
            return issue

    return None


def _sorted_driver_entry_points(entry_points: Iterable[Any] | None) -> tuple[Any, ...]:
    selected = _driver_entry_points() if entry_points is None else tuple(entry_points)
    return tuple(
        sorted(selected, key=lambda entry: (_entry_point_name(entry), _entry_point_value(entry)))
    )


def _driver_entry_points() -> tuple[Any, ...]:
    all_entry_points = metadata.entry_points()
    if hasattr(all_entry_points, "select"):
        return tuple(all_entry_points.select(group=ENTRY_POINT_GROUP))
    return tuple(all_entry_points.get(ENTRY_POINT_GROUP, ()))


def _load_plugin_descriptor(entry_point: Any) -> PluginDescriptor:
    loaded = entry_point.load()
    return _coerce_plugin_descriptor(loaded)


def _coerce_plugin_descriptor(value: Any) -> PluginDescriptor:
    if isinstance(value, PluginDescriptor):
        return value

    if hasattr(value, "get_plugin_descriptor"):
        descriptor = value.get_plugin_descriptor()
        if isinstance(descriptor, PluginDescriptor):
            return descriptor

    if callable(value):
        descriptor = value()
        if isinstance(descriptor, PluginDescriptor):
            return descriptor
        if hasattr(descriptor, "get_plugin_descriptor"):
            plugin_descriptor = descriptor.get_plugin_descriptor()
            if isinstance(plugin_descriptor, PluginDescriptor):
                return plugin_descriptor

    raise TypeError("Driver entry point must return a PluginDescriptor")


def _duplicate_driver_type_issue(
    driver_type: str,
    entry_point_names: Sequence[str],
    *,
    entry_point_name: str,
    entry_point_value: str,
) -> DriverDiscoveryIssue:
    listed = ", ".join(entry_point_names)
    return DriverDiscoveryIssue(
        issue=DriverIssue(
            category=DriverIssueCategory.DUPLICATE_DRIVER_TYPE.value,
            message=f"Duplicate driver type {driver_type!r} registered by: {listed}",
            path=f"entry_points.{ENTRY_POINT_GROUP}.{driver_type}",
        ),
        entry_point_name=entry_point_name,
        entry_point_value=entry_point_value,
        driver_type=driver_type,
    )


def _entry_point_name(entry_point: Any) -> str:
    return str(getattr(entry_point, "name", "<unknown>"))


def _entry_point_value(entry_point: Any) -> str:
    return str(getattr(entry_point, "value", "<unknown>"))


def _suggest_install_command(driver_type: str) -> str:
    if driver_type.startswith("mock_"):
        return "pip install workspace-fabric-driver-mock"
    normalized = driver_type.replace("_", "-")
    return f"pip install workspace-fabric-driver-{normalized}"
