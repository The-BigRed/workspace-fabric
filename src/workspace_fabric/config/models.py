from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class FabricConfig:
    id: str
    display_name: str | None = None
    description: str | None = None


@dataclass(frozen=True, slots=True)
class DriverConfig:
    id: str
    type: str
    fabric: str
    connection: dict[str, Any] = field(default_factory=dict)
    capabilities: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class HostConfig:
    id: str
    fabric: str
    display_name: str | None = None


@dataclass(frozen=True, slots=True)
class VideoSourceConfig:
    id: str
    fabric: str
    host: str
    display_name: str | None = None


@dataclass(frozen=True, slots=True)
class VideoOutputConfig:
    id: str
    fabric: str
    driver: str
    port: int


@dataclass(frozen=True, slots=True)
class DisplayConfig:
    id: str
    fabric: str
    output: str
    display_name: str | None = None


@dataclass(frozen=True, slots=True)
class UsbMatrixConfig:
    id: str
    fabric: str
    driver: str
    hosts: dict[int, str]


@dataclass(frozen=True, slots=True)
class UsbDeviceConfig:
    id: str
    fabric: str
    matrix: str
    device_port: int
    display_name: str | None = None


@dataclass(frozen=True, slots=True)
class RemoteConsoleConfig:
    id: str
    fabric: str
    driver: str
    display_name: str | None = None


@dataclass(frozen=True, slots=True)
class CapabilityRequestConfig:
    name: str
    policy: str | None
    options: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class WorkspaceVideoRouteConfig:
    source: str
    capabilities: dict[str, CapabilityRequestConfig] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class WorkspaceConfig:
    id: str
    fabric: str
    display_name: str | None = None
    video: dict[str, WorkspaceVideoRouteConfig] = field(default_factory=dict)
    usb: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class WorkspaceFabricConfig:
    version: int
    fabrics: dict[str, FabricConfig] = field(default_factory=dict)
    drivers: dict[str, DriverConfig] = field(default_factory=dict)
    hosts: dict[str, HostConfig] = field(default_factory=dict)
    video_sources: dict[str, VideoSourceConfig] = field(default_factory=dict)
    video_outputs: dict[str, VideoOutputConfig] = field(default_factory=dict)
    displays: dict[str, DisplayConfig] = field(default_factory=dict)
    usb_matrices: dict[str, UsbMatrixConfig] = field(default_factory=dict)
    usb_devices: dict[str, UsbDeviceConfig] = field(default_factory=dict)
    remote_consoles: dict[str, RemoteConsoleConfig] = field(default_factory=dict)
    workspaces: dict[str, WorkspaceConfig] = field(default_factory=dict)
