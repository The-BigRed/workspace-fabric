from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from workspace_fabric_driver_api.types import (
    Driver,
    DriverIssue,
    DriverIssueCategory,
    DriverValidationResult,
)

DriverFactory = Callable[[Any], Driver]


@dataclass(frozen=True, order=True, slots=True)
class ApiCompatibilityVersion:
    """Driver API compatibility version, independent of package versions.

    Compatibility follows semantic-version major/minor rules: a driver declaring
    API 1.0 is compatible with a core accepting API 1.1, but a driver declaring
    API 1.1 is not compatible with a core accepting only API 1.0.
    """

    major: int
    minor: int = 0
    patch: int = 0

    def __post_init__(self) -> None:
        for name, value in (
            ("major", self.major),
            ("minor", self.minor),
            ("patch", self.patch),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"Driver API {name} version must be a non-negative integer")

    @classmethod
    def parse(cls, value: ApiCompatibilityVersion | str) -> ApiCompatibilityVersion:
        if isinstance(value, cls):
            return value
        if not isinstance(value, str):
            raise TypeError("Driver API compatibility version must be a string")

        parts = value.split(".")
        if len(parts) not in {2, 3}:
            raise ValueError(
                "Driver API compatibility version must use 'major.minor' " "or 'major.minor.patch'"
            )
        if any(part == "" or not part.isdecimal() for part in parts):
            raise ValueError(
                "Driver API compatibility version must contain only numeric components"
            )

        major, minor, *patch = (int(part) for part in parts)
        return cls(major, minor, patch[0] if patch else 0)

    def is_compatible_with(self, accepted_version: ApiCompatibilityVersion | str) -> bool:
        accepted = self.parse(accepted_version)
        return self.major == accepted.major and self.minor <= accepted.minor

    def __str__(self) -> str:
        if self.patch:
            return f"{self.major}.{self.minor}.{self.patch}"
        return f"{self.major}.{self.minor}"


DRIVER_API_COMPATIBILITY_VERSION = ApiCompatibilityVersion(1, 0)


@dataclass(frozen=True, slots=True)
class PluginDescriptor:
    driver_type: str
    display_name: str
    driver_version: str
    supported_driver_api: ApiCompatibilityVersion | str
    factory: DriverFactory
    configuration_schema: Mapping[str, Any] = field(default_factory=dict)
    port_metadata: Mapping[str, Any] = field(default_factory=dict)
    capability_metadata: Mapping[str, Any] = field(default_factory=dict)
    is_mock: bool = False
    package_name: str | None = None

    def __post_init__(self) -> None:
        if not self.driver_type:
            raise ValueError("Plugin descriptor driver_type is required")
        if not self.display_name:
            raise ValueError("Plugin descriptor display_name is required")
        if not self.driver_version:
            raise ValueError("Plugin descriptor driver_version is required")
        if not callable(self.factory):
            raise TypeError("Plugin descriptor factory must be callable")

        object.__setattr__(
            self,
            "supported_driver_api",
            ApiCompatibilityVersion.parse(self.supported_driver_api),
        )


@runtime_checkable
class DriverPlugin(Protocol):
    def get_plugin_descriptor(self) -> PluginDescriptor: ...


def validate_driver_api_compatibility(
    descriptor: PluginDescriptor,
    accepted_version: ApiCompatibilityVersion | str = DRIVER_API_COMPATIBILITY_VERSION,
) -> DriverValidationResult:
    accepted = ApiCompatibilityVersion.parse(accepted_version)
    if descriptor.supported_driver_api.is_compatible_with(accepted):
        return DriverValidationResult(valid=True)

    issue = DriverIssue(
        category=DriverIssueCategory.INCOMPATIBLE_DRIVER_API.value,
        message=(
            f"Driver {descriptor.driver_type!r} version {descriptor.driver_version!r} "
            f"supports Driver API {descriptor.supported_driver_api}; "
            f"core accepts Driver API {accepted}"
        ),
        path=f"$.drivers.{descriptor.driver_type}.driver_api",
    )
    return DriverValidationResult(valid=False, errors=(issue,))
