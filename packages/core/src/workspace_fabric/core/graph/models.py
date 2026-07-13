from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from workspace_fabric.config.models import (
    DisplayConfig,
    DriverConfig,
    HostConfig,
    UsbDeviceConfig,
    UsbMatrixConfig,
    VideoOutputConfig,
    VideoSourceConfig,
    WorkspaceFabricConfig,
)
from workspace_fabric.core.graph.errors import ResourceGraphError, ResourceGraphIssue


class ResourceKind(StrEnum):
    FABRIC = "fabric"
    DRIVER = "driver"
    HOST = "host"
    VIDEO_SOURCE = "video_source"
    VIDEO_OUTPUT = "video_output"
    DISPLAY = "display"
    USB_MATRIX = "usb_matrix"
    USB_DEVICE = "usb_device"
    REMOTE_CONSOLE = "remote_console"
    WORKSPACE = "workspace"


@dataclass(frozen=True, slots=True)
class ResourceNode:
    id: str
    kind: ResourceKind
    fabric: str | None


@dataclass(frozen=True, slots=True)
class ResourceEdge:
    source: tuple[ResourceKind, str]
    target: tuple[ResourceKind, str]
    relationship: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class UsbRouteResolution:
    device: UsbDeviceConfig
    host: HostConfig
    matrix: UsbMatrixConfig
    device_port: int
    host_port: int
    driver: DriverConfig


@dataclass(frozen=True, slots=True)
class VideoRouteResolution:
    display: DisplayConfig
    source: VideoSourceConfig
    output: VideoOutputConfig
    driver: DriverConfig
    source_host: HostConfig
    input_port: int | None
    output_port: int


@dataclass(frozen=True, slots=True)
class ResourceGraph:
    config: WorkspaceFabricConfig
    nodes: dict[tuple[ResourceKind, str], ResourceNode]
    edges: tuple[ResourceEdge, ...]

    def get_node(self, kind: ResourceKind, resource_id: str) -> ResourceNode | None:
        return self.nodes.get((kind, resource_id))

    def usb_host_map(self, matrix_id: str) -> dict[int, str]:
        matrix = self.config.usb_matrices[matrix_id]
        return dict(matrix.hosts)

    def can_route_usb_device_to_host(self, device_id: str, host_id: str) -> bool:
        try:
            self.resolve_usb_route(device_id, host_id)
        except ResourceGraphError:
            return False
        return True

    def resolve_usb_route(self, device_id: str, host_id: str) -> UsbRouteResolution:
        device = self.config.usb_devices.get(device_id)
        host = self.config.hosts.get(host_id)
        if device is None:
            raise ResourceGraphError(
                [ResourceGraphIssue("$.usb_devices", f"Unknown USB device {device_id!r}")]
            )
        if host is None:
            raise ResourceGraphError([ResourceGraphIssue("$.hosts", f"Unknown host {host_id!r}")])

        matrix = self.config.usb_matrices[device.matrix]
        matching_ports = [
            port for port, attached_host in matrix.hosts.items() if attached_host == host_id
        ]
        if not matching_ports:
            raise ResourceGraphError(
                [
                    ResourceGraphIssue(
                        f"$.usb_matrices.{matrix.id}.hosts",
                        (
                            f"Host {host_id!r} is not attached to USB matrix {matrix.id!r} "
                            f"for USB device {device_id!r}"
                        ),
                    )
                ]
            )

        return UsbRouteResolution(
            device=device,
            host=host,
            matrix=matrix,
            device_port=device.device_port,
            host_port=matching_ports[0],
            driver=self.config.drivers[matrix.driver],
        )

    def resolve_video_route(self, display_id: str, source_id: str) -> VideoRouteResolution:
        display = self.config.displays.get(display_id)
        source = self.config.video_sources.get(source_id)
        if display is None:
            raise ResourceGraphError(
                [ResourceGraphIssue("$.displays", f"Unknown display {display_id!r}")]
            )
        if source is None:
            raise ResourceGraphError(
                [ResourceGraphIssue("$.video_sources", f"Unknown video source {source_id!r}")]
            )

        output = self.config.video_outputs[display.output]
        if source.driver is not None and source.driver != output.driver:
            raise ResourceGraphError(
                [
                    ResourceGraphIssue(
                        f"$.video_sources.{source.id}.driver",
                        (
                            f"Video source {source.id!r} is attached to driver "
                            f"{source.driver!r}, but display {display.id!r} is attached to "
                            f"driver {output.driver!r}"
                        ),
                    )
                ]
            )

        return VideoRouteResolution(
            display=display,
            source=source,
            output=output,
            driver=self.config.drivers[output.driver],
            source_host=self.config.hosts[source.host],
            input_port=source.port,
            output_port=output.port,
        )

    def dump(self) -> dict[str, Any]:
        return {
            "resources": self._dump_resources(),
            "relationships": self._dump_relationships(),
        }

    def _dump_resources(self) -> dict[str, Any]:
        return {
            "fabrics": sorted(self.config.fabrics),
            "drivers": {
                driver_id: {
                    "fabric": driver.fabric,
                    "type": driver.type,
                    "capabilities": dict(sorted(driver.capabilities.items())),
                }
                for driver_id, driver in sorted(self.config.drivers.items())
            },
            "hosts": sorted(self.config.hosts),
            "video_sources": sorted(self.config.video_sources),
            "video_outputs": sorted(self.config.video_outputs),
            "displays": sorted(self.config.displays),
            "usb_matrices": sorted(self.config.usb_matrices),
            "usb_devices": sorted(self.config.usb_devices),
            "remote_consoles": sorted(self.config.remote_consoles),
            "workspaces": sorted(self.config.workspaces),
        }

    def _dump_relationships(self) -> dict[str, Any]:
        return {
            "video_sources": {
                source_id: {
                    key: value
                    for key, value in {
                        "host": source.host,
                        "driver": source.driver,
                        "port": source.port,
                    }.items()
                    if value is not None
                }
                for source_id, source in sorted(self.config.video_sources.items())
            },
            "displays": {
                display_id: {
                    "output": display.output,
                    "driver": self.config.video_outputs[display.output].driver,
                }
                for display_id, display in sorted(self.config.displays.items())
            },
            "usb_matrices": {
                matrix_id: {
                    "driver": matrix.driver,
                    "hosts": dict(sorted(matrix.hosts.items())),
                }
                for matrix_id, matrix in sorted(self.config.usb_matrices.items())
            },
            "usb_devices": {
                device_id: {
                    "matrix": device.matrix,
                    "device_port": device.device_port,
                    "driver": self.config.usb_matrices[device.matrix].driver,
                }
                for device_id, device in sorted(self.config.usb_devices.items())
            },
            "workspaces": {
                workspace_id: {
                    "video": {
                        display_id: route.source
                        for display_id, route in sorted(workspace.video.items())
                    },
                    "usb": dict(sorted(workspace.usb.items())),
                }
                for workspace_id, workspace in sorted(self.config.workspaces.items())
            },
        }
