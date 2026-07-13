"""Workspace Fabric Driver API - Portable driver contracts and interfaces."""

from workspace_fabric_driver_api.plugin import (
    DRIVER_API_COMPATIBILITY_VERSION,
    ApiCompatibilityVersion,
    DriverFactory,
    DriverPlugin,
    PluginDescriptor,
    validate_driver_api_compatibility,
)
from workspace_fabric_driver_api.types import (
    Driver,
    DriverAction,
    DriverActionPlan,
    DriverActionResult,
    DriverActionStatus,
    DriverActionType,
    DriverCapabilityStatus,
    DriverHealth,
    DriverHealthStatus,
    DriverIssue,
    DriverIssueCategory,
    DriverObservedStateStatus,
    DriverValidationResult,
    UsbMatrixDriver,
    VideoMatrixDriver,
)

__version__ = "1.0.0"

__all__ = [
    "DRIVER_API_COMPATIBILITY_VERSION",
    "ApiCompatibilityVersion",
    "Driver",
    "DriverAction",
    "DriverActionPlan",
    "DriverActionResult",
    "DriverActionStatus",
    "DriverActionType",
    "DriverCapabilityStatus",
    "DriverHealth",
    "DriverHealthStatus",
    "DriverFactory",
    "DriverIssue",
    "DriverIssueCategory",
    "DriverObservedStateStatus",
    "DriverPlugin",
    "DriverValidationResult",
    "PluginDescriptor",
    "UsbMatrixDriver",
    "VideoMatrixDriver",
    "validate_driver_api_compatibility",
]
