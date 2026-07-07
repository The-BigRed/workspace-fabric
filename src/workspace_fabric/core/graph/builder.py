from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from workspace_fabric.config.models import WorkspaceConfig, WorkspaceFabricConfig
from workspace_fabric.core.graph.errors import ResourceGraphError, ResourceGraphIssue
from workspace_fabric.core.graph.models import (
    ResourceEdge,
    ResourceGraph,
    ResourceKind,
    ResourceNode,
)


def build_resource_graph(config: WorkspaceFabricConfig) -> ResourceGraph:
    return _ResourceGraphBuilder(config).build()


@dataclass(frozen=True, slots=True)
class _ResourceCollection:
    kind: ResourceKind
    path: str
    resources: Mapping[str, Any]


class _ResourceGraphBuilder:
    def __init__(self, config: WorkspaceFabricConfig) -> None:
        self._config = config
        self._issues: list[ResourceGraphIssue] = []
        self._nodes: dict[tuple[ResourceKind, str], ResourceNode] = {}
        self._edges: list[ResourceEdge] = []

    def build(self) -> ResourceGraph:
        self._add_nodes()
        self._validate_and_add_edges()
        self._raise_if_invalid()
        return ResourceGraph(
            config=self._config,
            nodes=dict(self._nodes),
            edges=tuple(self._edges),
        )

    def _add_nodes(self) -> None:
        for collection in self._collections():
            seen_ids: set[str] = set()
            for resource_key, resource in collection.resources.items():
                resource_id = resource.id
                path = f"{collection.path}.{resource_key}"
                if resource_id != resource_key:
                    self._add_issue(
                        path,
                        f"Resource key {resource_key!r} does not match resource id {resource_id!r}",
                    )
                if resource_id in seen_ids:
                    self._add_issue(
                        path,
                        f"Duplicate {collection.kind.value} ID {resource_id!r}",
                    )
                    continue

                seen_ids.add(resource_id)
                fabric = resource_id if collection.kind is ResourceKind.FABRIC else resource.fabric
                self._nodes[(collection.kind, resource_id)] = ResourceNode(
                    id=resource_id,
                    kind=collection.kind,
                    fabric=fabric,
                )

    def _collections(self) -> tuple[_ResourceCollection, ...]:
        return (
            _ResourceCollection(ResourceKind.FABRIC, "$.fabrics", self._config.fabrics),
            _ResourceCollection(ResourceKind.DRIVER, "$.drivers", self._config.drivers),
            _ResourceCollection(ResourceKind.HOST, "$.hosts", self._config.hosts),
            _ResourceCollection(
                ResourceKind.VIDEO_SOURCE,
                "$.video_sources",
                self._config.video_sources,
            ),
            _ResourceCollection(
                ResourceKind.VIDEO_OUTPUT,
                "$.video_outputs",
                self._config.video_outputs,
            ),
            _ResourceCollection(ResourceKind.DISPLAY, "$.displays", self._config.displays),
            _ResourceCollection(
                ResourceKind.USB_MATRIX,
                "$.usb_matrices",
                self._config.usb_matrices,
            ),
            _ResourceCollection(
                ResourceKind.USB_DEVICE,
                "$.usb_devices",
                self._config.usb_devices,
            ),
            _ResourceCollection(
                ResourceKind.REMOTE_CONSOLE,
                "$.remote_consoles",
                self._config.remote_consoles,
            ),
            _ResourceCollection(ResourceKind.WORKSPACE, "$.workspaces", self._config.workspaces),
        )

    def _validate_and_add_edges(self) -> None:
        self._validate_drivers()
        self._validate_hosts()
        self._validate_video_sources()
        self._validate_video_outputs()
        self._validate_displays()
        self._validate_usb_matrices()
        self._validate_usb_devices()
        self._validate_remote_consoles()
        self._validate_workspaces()

    def _validate_drivers(self) -> None:
        for driver in self._config.drivers.values():
            self._require_fabric(driver.fabric, f"$.drivers.{driver.id}.fabric")

    def _validate_hosts(self) -> None:
        for host in self._config.hosts.values():
            self._require_fabric(host.fabric, f"$.hosts.{host.id}.fabric")

    def _validate_video_sources(self) -> None:
        for source in self._config.video_sources.values():
            path = f"$.video_sources.{source.id}"
            self._require_fabric(source.fabric, f"{path}.fabric")
            host = self._require_resource(
                ResourceKind.HOST,
                source.host,
                f"{path}.host",
                "host",
            )
            if host is not None:
                self._require_same_fabric(source.fabric, host.fabric, f"{path}.host", "host")
                self._add_edge(
                    ResourceKind.VIDEO_SOURCE,
                    source.id,
                    ResourceKind.HOST,
                    source.host,
                    "source_host",
                )

    def _validate_video_outputs(self) -> None:
        for output in self._config.video_outputs.values():
            path = f"$.video_outputs.{output.id}"
            self._require_fabric(output.fabric, f"{path}.fabric")
            driver = self._require_resource(
                ResourceKind.DRIVER,
                output.driver,
                f"{path}.driver",
                "driver",
            )
            if driver is not None:
                self._require_same_fabric(output.fabric, driver.fabric, f"{path}.driver", "driver")
                self._add_edge(
                    ResourceKind.VIDEO_OUTPUT,
                    output.id,
                    ResourceKind.DRIVER,
                    output.driver,
                    "owned_by_driver",
                )

    def _validate_displays(self) -> None:
        for display in self._config.displays.values():
            path = f"$.displays.{display.id}"
            self._require_fabric(display.fabric, f"{path}.fabric")
            output = self._require_resource(
                ResourceKind.VIDEO_OUTPUT,
                display.output,
                f"{path}.output",
                "video output",
            )
            if output is not None:
                self._require_same_fabric(
                    display.fabric,
                    output.fabric,
                    f"{path}.output",
                    "video output",
                )
                self._add_edge(
                    ResourceKind.DISPLAY,
                    display.id,
                    ResourceKind.VIDEO_OUTPUT,
                    display.output,
                    "fed_by_output",
                )

    def _validate_usb_matrices(self) -> None:
        for matrix in self._config.usb_matrices.values():
            path = f"$.usb_matrices.{matrix.id}"
            self._require_fabric(matrix.fabric, f"{path}.fabric")
            driver = self._require_resource(
                ResourceKind.DRIVER,
                matrix.driver,
                f"{path}.driver",
                "driver",
            )
            if driver is not None:
                self._require_same_fabric(matrix.fabric, driver.fabric, f"{path}.driver", "driver")
                self._add_edge(
                    ResourceKind.USB_MATRIX,
                    matrix.id,
                    ResourceKind.DRIVER,
                    matrix.driver,
                    "owned_by_driver",
                )

            for port, host_id in matrix.hosts.items():
                host = self._require_resource(
                    ResourceKind.HOST,
                    host_id,
                    f"{path}.hosts.{port}",
                    "host",
                )
                if host is not None:
                    self._require_same_fabric(
                        matrix.fabric, host.fabric, f"{path}.hosts.{port}", "host"
                    )
                    self._add_edge(
                        ResourceKind.USB_MATRIX,
                        matrix.id,
                        ResourceKind.HOST,
                        host_id,
                        "host_attachment",
                        {"port": port},
                    )

    def _validate_usb_devices(self) -> None:
        for device in self._config.usb_devices.values():
            path = f"$.usb_devices.{device.id}"
            self._require_fabric(device.fabric, f"{path}.fabric")
            matrix = self._require_resource(
                ResourceKind.USB_MATRIX,
                device.matrix,
                f"{path}.matrix",
                "USB matrix",
            )
            if matrix is not None:
                self._require_same_fabric(
                    device.fabric,
                    matrix.fabric,
                    f"{path}.matrix",
                    "USB matrix",
                )
                self._add_edge(
                    ResourceKind.USB_DEVICE,
                    device.id,
                    ResourceKind.USB_MATRIX,
                    device.matrix,
                    "attached_to_matrix",
                    {"device_port": device.device_port},
                )

    def _validate_remote_consoles(self) -> None:
        for remote_console in self._config.remote_consoles.values():
            path = f"$.remote_consoles.{remote_console.id}"
            self._require_fabric(remote_console.fabric, f"{path}.fabric")
            driver = self._require_resource(
                ResourceKind.DRIVER,
                remote_console.driver,
                f"{path}.driver",
                "driver",
            )
            if driver is not None:
                self._require_same_fabric(
                    remote_console.fabric,
                    driver.fabric,
                    f"{path}.driver",
                    "driver",
                )
                self._add_edge(
                    ResourceKind.REMOTE_CONSOLE,
                    remote_console.id,
                    ResourceKind.DRIVER,
                    remote_console.driver,
                    "owned_by_driver",
                )

    def _validate_workspaces(self) -> None:
        for workspace in self._config.workspaces.values():
            path = f"$.workspaces.{workspace.id}"
            self._require_fabric(workspace.fabric, f"{path}.fabric")
            self._validate_workspace_video_routes(workspace, path)
            self._validate_workspace_usb_routes(workspace, path)

    def _validate_workspace_video_routes(self, workspace: WorkspaceConfig, path: str) -> None:
        for display_id, route in workspace.video.items():
            route_path = f"{path}.video.{display_id}"
            display = self._require_resource(
                ResourceKind.DISPLAY,
                display_id,
                route_path,
                "display",
            )
            source = self._require_resource(
                ResourceKind.VIDEO_SOURCE,
                route.source,
                f"{route_path}.source",
                "video source",
            )
            if display is not None:
                self._require_same_fabric(workspace.fabric, display.fabric, route_path, "display")
            if source is not None:
                self._require_same_fabric(
                    workspace.fabric,
                    source.fabric,
                    f"{route_path}.source",
                    "video source",
                )
            if display is not None and source is not None:
                self._add_edge(
                    ResourceKind.WORKSPACE,
                    workspace.id,
                    ResourceKind.DISPLAY,
                    display_id,
                    "workspace_video_display",
                    {"source": route.source},
                )
                self._add_edge(
                    ResourceKind.WORKSPACE,
                    workspace.id,
                    ResourceKind.VIDEO_SOURCE,
                    route.source,
                    "workspace_video_source",
                    {"display": display_id},
                )

    def _validate_workspace_usb_routes(self, workspace: WorkspaceConfig, path: str) -> None:
        for device_id, host_id in workspace.usb.items():
            route_path = f"{path}.usb.{device_id}"
            device_node = self._require_resource(
                ResourceKind.USB_DEVICE,
                device_id,
                route_path,
                "USB device",
            )
            host_node = self._require_resource(ResourceKind.HOST, host_id, route_path, "host")
            if device_node is None or host_node is None:
                continue

            self._require_same_fabric(
                workspace.fabric,
                device_node.fabric,
                route_path,
                "USB device",
            )
            self._require_same_fabric(workspace.fabric, host_node.fabric, route_path, "host")
            device = self._config.usb_devices[device_id]
            matrix = self._config.usb_matrices.get(device.matrix)
            if matrix is None:
                continue

            if host_id not in matrix.hosts.values():
                self._add_issue(
                    route_path,
                    (
                        f"Host {host_id!r} is not attached to USB matrix {matrix.id!r} "
                        f"for USB device {device_id!r}"
                    ),
                )
                continue

            self._add_edge(
                ResourceKind.WORKSPACE,
                workspace.id,
                ResourceKind.USB_DEVICE,
                device_id,
                "workspace_usb_device",
                {"host": host_id},
            )
            self._add_edge(
                ResourceKind.WORKSPACE,
                workspace.id,
                ResourceKind.HOST,
                host_id,
                "workspace_usb_host",
                {"device": device_id},
            )

    def _require_fabric(self, fabric_id: str, path: str) -> ResourceNode | None:
        return self._require_node(ResourceKind.FABRIC, fabric_id, path, "fabric")

    def _require_resource(
        self,
        kind: ResourceKind,
        resource_id: str,
        path: str,
        resource_type: str,
    ) -> ResourceNode | None:
        return self._require_node(kind, resource_id, path, resource_type)

    def _require_node(
        self,
        kind: ResourceKind,
        resource_id: str,
        path: str,
        resource_type: str,
    ) -> ResourceNode | None:
        node = self._nodes.get((kind, resource_id))
        if node is not None:
            return node

        self._add_issue(path, f"Unknown {resource_type} reference {resource_id!r}")
        return None

    def _require_same_fabric(
        self,
        owner_fabric: str | None,
        referenced_fabric: str | None,
        path: str,
        resource_type: str,
    ) -> None:
        if owner_fabric != referenced_fabric:
            self._add_issue(
                path,
                (
                    f"Referenced {resource_type} belongs to fabric {referenced_fabric!r}, "
                    f"expected {owner_fabric!r}"
                ),
            )

    def _add_edge(
        self,
        source_kind: ResourceKind,
        source_id: str,
        target_kind: ResourceKind,
        target_id: str,
        relationship: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self._edges.append(
            ResourceEdge(
                source=(source_kind, source_id),
                target=(target_kind, target_id),
                relationship=relationship,
                metadata=metadata or {},
            )
        )

    def _add_issue(self, path: str, message: str) -> None:
        self._issues.append(ResourceGraphIssue(path, message))

    def _raise_if_invalid(self) -> None:
        if self._issues:
            raise ResourceGraphError(self._issues)
