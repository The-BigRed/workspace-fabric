from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

from workspace_fabric.config.errors import ConfigValidationError, ConfigValidationIssue
from workspace_fabric.config.models import (
    CapabilityRequestConfig,
    DisplayConfig,
    DriverConfig,
    FabricConfig,
    HostConfig,
    RemoteConsoleConfig,
    UsbDeviceConfig,
    UsbMatrixConfig,
    VideoOutputConfig,
    VideoSourceConfig,
    WorkspaceConfig,
    WorkspaceFabricConfig,
    WorkspaceVideoRouteConfig,
)

SCHEMA_VERSION = 1

CAPABILITY_POLICIES = frozenset({"ignore", "prefer", "require", "disable"})
CAPABILITY_STATUSES = frozenset({"supported", "unsupported", "unknown"})
TOP_LEVEL_SECTIONS = frozenset(
    {
        "version",
        "fabrics",
        "drivers",
        "hosts",
        "video_sources",
        "video_outputs",
        "displays",
        "usb_matrices",
        "usb_devices",
        "remote_consoles",
        "workspaces",
    }
)


class _UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_mapping_without_duplicates(
    loader: _UniqueKeyLoader,
    node: yaml.MappingNode,
    deep: bool = False,
) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    mapping: dict[Any, Any] = {}

    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)

    return mapping


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_mapping_without_duplicates,
)


def load_config(path: str | Path) -> WorkspaceFabricConfig:
    config_path = Path(path)

    try:
        text = config_path.read_text(encoding="utf-8")
    except OSError as exc:
        issue = ConfigValidationIssue("$", f"Could not read configuration file: {exc}")
        raise ConfigValidationError([issue]) from exc

    return load_config_text(text, source=str(config_path))


def load_config_text(text: str, *, source: str = "<string>") -> WorkspaceFabricConfig:
    try:
        raw_config = yaml.load(text, Loader=_UniqueKeyLoader)
    except yaml.YAMLError as exc:
        issue = ConfigValidationIssue("$", f"Invalid YAML in {source}: {_format_yaml_error(exc)}")
        raise ConfigValidationError([issue]) from exc

    parser = _ConfigParser()
    return parser.parse(raw_config)


def _format_yaml_error(error: yaml.YAMLError) -> str:
    problem = getattr(error, "problem", None)
    problem_mark = getattr(error, "problem_mark", None)

    if problem and problem_mark:
        return f"{problem} at line {problem_mark.line + 1}, column {problem_mark.column + 1}"
    if problem:
        return str(problem)
    return str(error)


class _ConfigParser:
    def __init__(self) -> None:
        self._issues: list[ConfigValidationIssue] = []

    def parse(self, raw_config: Any) -> WorkspaceFabricConfig:
        if raw_config is None:
            self._add_issue("$", "Configuration file is empty")
            self._raise_if_invalid()
            return self._empty_config()

        if not isinstance(raw_config, Mapping):
            self._add_issue("$", "Configuration root must be a mapping")
            self._raise_if_invalid()
            return self._empty_config()

        for key in raw_config:
            if not isinstance(key, str):
                self._add_issue("$", f"Top-level key {key!r} must be a string")
            elif key not in TOP_LEVEL_SECTIONS:
                self._add_issue(f"$.{key}", f"Unknown top-level section {key!r}")

        version = self._parse_version(raw_config)

        fabrics = self._parse_section("fabrics", raw_config, self._parse_fabric)
        drivers = self._parse_section("drivers", raw_config, self._parse_driver)
        hosts = self._parse_section("hosts", raw_config, self._parse_host)
        video_sources = self._parse_section(
            "video_sources",
            raw_config,
            self._parse_video_source,
        )
        video_outputs = self._parse_section(
            "video_outputs",
            raw_config,
            self._parse_video_output,
        )
        displays = self._parse_section("displays", raw_config, self._parse_display)
        usb_matrices = self._parse_section(
            "usb_matrices",
            raw_config,
            self._parse_usb_matrix,
        )
        usb_devices = self._parse_section("usb_devices", raw_config, self._parse_usb_device)
        remote_consoles = self._parse_section(
            "remote_consoles",
            raw_config,
            self._parse_remote_console,
        )
        workspaces = self._parse_section("workspaces", raw_config, self._parse_workspace)

        self._raise_if_invalid()

        return WorkspaceFabricConfig(
            version=version,
            fabrics=fabrics,
            drivers=drivers,
            hosts=hosts,
            video_sources=video_sources,
            video_outputs=video_outputs,
            displays=displays,
            usb_matrices=usb_matrices,
            usb_devices=usb_devices,
            remote_consoles=remote_consoles,
            workspaces=workspaces,
        )

    def _parse_version(self, raw_config: Mapping[Any, Any]) -> int:
        if "version" not in raw_config:
            self._add_issue("$.version", "Required field is missing")
            return SCHEMA_VERSION

        version = raw_config["version"]
        if not self._is_int(version):
            self._add_issue("$.version", "Expected an integer schema version")
            return SCHEMA_VERSION
        if version != SCHEMA_VERSION:
            self._add_issue(
                "$.version",
                f"Unsupported schema version {version!r}; expected {SCHEMA_VERSION}",
            )
        return version

    def _parse_section(
        self,
        section: str,
        raw_config: Mapping[Any, Any],
        parser: Any,
    ) -> dict[str, Any]:
        raw_section = raw_config.get(section, {})
        path = f"$.{section}"

        if not isinstance(raw_section, Mapping):
            self._add_issue(path, "Expected a mapping of IDs to definitions")
            return {}

        parsed: dict[str, Any] = {}
        for raw_id, raw_item in raw_section.items():
            if not isinstance(raw_id, str):
                self._add_issue(path, f"Resource ID {raw_id!r} must be a string")
                continue

            item_path = f"{path}.{raw_id}"
            if not isinstance(raw_item, Mapping):
                self._add_issue(item_path, "Expected a mapping")
                continue

            parsed[raw_id] = parser(raw_id, raw_item, item_path)

        return parsed

    def _parse_fabric(
        self, resource_id: str, raw_item: Mapping[Any, Any], path: str
    ) -> FabricConfig:
        self._check_allowed_fields(raw_item, path, {"display_name", "description"})
        return FabricConfig(
            id=resource_id,
            display_name=self._optional_str(raw_item, path, "display_name"),
            description=self._optional_str(raw_item, path, "description"),
        )

    def _parse_driver(
        self, resource_id: str, raw_item: Mapping[Any, Any], path: str
    ) -> DriverConfig:
        self._check_allowed_fields(
            raw_item,
            path,
            {"type", "fabric", "connection", "capabilities"},
        )
        return DriverConfig(
            id=resource_id,
            type=self._required_str(raw_item, path, "type"),
            fabric=self._required_str(raw_item, path, "fabric"),
            connection=self._optional_mapping(raw_item, path, "connection"),
            capabilities=self._parse_driver_capabilities(raw_item, path),
        )

    def _parse_host(self, resource_id: str, raw_item: Mapping[Any, Any], path: str) -> HostConfig:
        self._check_allowed_fields(raw_item, path, {"fabric", "display_name"})
        return HostConfig(
            id=resource_id,
            fabric=self._required_str(raw_item, path, "fabric"),
            display_name=self._optional_str(raw_item, path, "display_name"),
        )

    def _parse_video_source(
        self,
        resource_id: str,
        raw_item: Mapping[Any, Any],
        path: str,
    ) -> VideoSourceConfig:
        self._check_allowed_fields(raw_item, path, {"fabric", "host", "display_name"})
        return VideoSourceConfig(
            id=resource_id,
            fabric=self._required_str(raw_item, path, "fabric"),
            host=self._required_str(raw_item, path, "host"),
            display_name=self._optional_str(raw_item, path, "display_name"),
        )

    def _parse_video_output(
        self,
        resource_id: str,
        raw_item: Mapping[Any, Any],
        path: str,
    ) -> VideoOutputConfig:
        self._check_allowed_fields(raw_item, path, {"fabric", "driver", "port"})
        return VideoOutputConfig(
            id=resource_id,
            fabric=self._required_str(raw_item, path, "fabric"),
            driver=self._required_str(raw_item, path, "driver"),
            port=self._required_positive_int(raw_item, path, "port"),
        )

    def _parse_display(
        self,
        resource_id: str,
        raw_item: Mapping[Any, Any],
        path: str,
    ) -> DisplayConfig:
        self._check_allowed_fields(raw_item, path, {"fabric", "display_name", "output"})
        return DisplayConfig(
            id=resource_id,
            fabric=self._required_str(raw_item, path, "fabric"),
            output=self._required_str(raw_item, path, "output"),
            display_name=self._optional_str(raw_item, path, "display_name"),
        )

    def _parse_usb_matrix(
        self,
        resource_id: str,
        raw_item: Mapping[Any, Any],
        path: str,
    ) -> UsbMatrixConfig:
        self._check_allowed_fields(raw_item, path, {"fabric", "driver", "hosts"})
        return UsbMatrixConfig(
            id=resource_id,
            fabric=self._required_str(raw_item, path, "fabric"),
            driver=self._required_str(raw_item, path, "driver"),
            hosts=self._parse_usb_hosts(raw_item, path),
        )

    def _parse_usb_device(
        self,
        resource_id: str,
        raw_item: Mapping[Any, Any],
        path: str,
    ) -> UsbDeviceConfig:
        self._check_allowed_fields(
            raw_item,
            path,
            {"fabric", "display_name", "matrix", "device_port"},
        )
        return UsbDeviceConfig(
            id=resource_id,
            fabric=self._required_str(raw_item, path, "fabric"),
            matrix=self._required_str(raw_item, path, "matrix"),
            device_port=self._required_positive_int(raw_item, path, "device_port"),
            display_name=self._optional_str(raw_item, path, "display_name"),
        )

    def _parse_remote_console(
        self,
        resource_id: str,
        raw_item: Mapping[Any, Any],
        path: str,
    ) -> RemoteConsoleConfig:
        self._check_allowed_fields(raw_item, path, {"fabric", "display_name", "driver"})
        return RemoteConsoleConfig(
            id=resource_id,
            fabric=self._required_str(raw_item, path, "fabric"),
            driver=self._required_str(raw_item, path, "driver"),
            display_name=self._optional_str(raw_item, path, "display_name"),
        )

    def _parse_workspace(
        self,
        resource_id: str,
        raw_item: Mapping[Any, Any],
        path: str,
    ) -> WorkspaceConfig:
        self._check_allowed_fields(raw_item, path, {"fabric", "display_name", "video", "usb"})
        return WorkspaceConfig(
            id=resource_id,
            fabric=self._required_str(raw_item, path, "fabric"),
            display_name=self._optional_str(raw_item, path, "display_name"),
            video=self._parse_workspace_video(raw_item, path),
            usb=self._parse_workspace_usb(raw_item, path),
        )

    def _parse_driver_capabilities(
        self,
        raw_item: Mapping[Any, Any],
        path: str,
    ) -> dict[str, str]:
        capabilities = self._optional_mapping(raw_item, path, "capabilities")
        parsed: dict[str, str] = {}

        for raw_name, raw_status in capabilities.items():
            capability_path = f"{path}.capabilities.{raw_name}"
            if not isinstance(raw_name, str):
                self._add_issue(
                    f"{path}.capabilities", f"Capability name {raw_name!r} must be a string"
                )
                continue
            if not isinstance(raw_status, str):
                self._add_issue(capability_path, "Capability status must be a string")
                continue
            if raw_status not in CAPABILITY_STATUSES:
                expected = ", ".join(sorted(CAPABILITY_STATUSES))
                self._add_issue(
                    capability_path,
                    f"Unknown capability status {raw_status!r}; expected one of {expected}",
                )
                continue

            parsed[raw_name] = raw_status

        return parsed

    def _parse_usb_hosts(self, raw_item: Mapping[Any, Any], path: str) -> dict[int, str]:
        raw_hosts = self._required_mapping(raw_item, path, "hosts")
        hosts: dict[int, str] = {}

        for raw_port, raw_host in raw_hosts.items():
            port_path = f"{path}.hosts.{raw_port}"
            port = self._parse_port_key(raw_port, f"{path}.hosts")
            if port is None:
                continue
            if port in hosts:
                self._add_issue(port_path, f"Duplicate USB host port {port!r}")
                continue
            if not isinstance(raw_host, str):
                self._add_issue(port_path, "USB host attachment must be a host ID string")
                continue

            hosts[port] = raw_host

        return hosts

    def _parse_workspace_video(
        self,
        raw_item: Mapping[Any, Any],
        path: str,
    ) -> dict[str, WorkspaceVideoRouteConfig]:
        raw_video = self._optional_mapping(raw_item, path, "video")
        parsed: dict[str, WorkspaceVideoRouteConfig] = {}

        for raw_display, raw_route in raw_video.items():
            route_path = f"{path}.video.{raw_display}"
            if not isinstance(raw_display, str):
                self._add_issue(f"{path}.video", f"Display ID {raw_display!r} must be a string")
                continue

            if isinstance(raw_route, str):
                parsed[raw_display] = WorkspaceVideoRouteConfig(source=raw_route)
                continue

            if not isinstance(raw_route, Mapping):
                self._add_issue(route_path, "Video route must be a source string or mapping")
                continue

            source = self._required_str(raw_route, route_path, "source")
            capabilities = self._parse_workspace_capabilities(raw_route, route_path)
            parsed[raw_display] = WorkspaceVideoRouteConfig(
                source=source,
                capabilities=capabilities,
            )

        return parsed

    def _parse_workspace_capabilities(
        self,
        raw_route: Mapping[Any, Any],
        path: str,
    ) -> dict[str, CapabilityRequestConfig]:
        capabilities: dict[str, CapabilityRequestConfig] = {}

        for raw_name, raw_request in raw_route.items():
            if raw_name == "source":
                continue

            capability_path = f"{path}.{raw_name}"
            if not isinstance(raw_name, str):
                self._add_issue(path, f"Capability name {raw_name!r} must be a string")
                continue
            if not isinstance(raw_request, Mapping):
                self._add_issue(capability_path, "Capability request must be a mapping")
                continue

            policy = raw_request.get("policy")
            if policy is not None:
                if not isinstance(policy, str):
                    self._add_issue(
                        f"{capability_path}.policy", "Capability policy must be a string"
                    )
                    continue
                if policy not in CAPABILITY_POLICIES:
                    expected = ", ".join(sorted(CAPABILITY_POLICIES))
                    self._add_issue(
                        f"{capability_path}.policy",
                        f"Unknown capability policy {policy!r}; expected one of {expected}",
                    )
                    continue

            capabilities[raw_name] = CapabilityRequestConfig(
                name=raw_name,
                policy=policy,
                options=dict(raw_request),
            )

        return capabilities

    def _parse_workspace_usb(
        self,
        raw_item: Mapping[Any, Any],
        path: str,
    ) -> dict[str, str]:
        raw_usb = self._optional_mapping(raw_item, path, "usb")
        parsed: dict[str, str] = {}

        for raw_device, raw_host in raw_usb.items():
            route_path = f"{path}.usb.{raw_device}"
            if not isinstance(raw_device, str):
                self._add_issue(f"{path}.usb", f"USB device ID {raw_device!r} must be a string")
                continue
            if not isinstance(raw_host, str):
                self._add_issue(route_path, "USB route target must be a host ID string")
                continue

            parsed[raw_device] = raw_host

        return parsed

    def _required_str(self, raw_item: Mapping[Any, Any], path: str, field_name: str) -> str:
        value = self._required_field(raw_item, path, field_name)
        if value is None:
            return ""
        if not isinstance(value, str):
            self._add_issue(f"{path}.{field_name}", "Expected a string")
            return ""
        return value

    def _optional_str(self, raw_item: Mapping[Any, Any], path: str, field_name: str) -> str | None:
        if field_name not in raw_item:
            return None
        value = raw_item[field_name]
        if value is None:
            return None
        if not isinstance(value, str):
            self._add_issue(f"{path}.{field_name}", "Expected a string")
            return None
        return value

    def _required_positive_int(
        self, raw_item: Mapping[Any, Any], path: str, field_name: str
    ) -> int:
        value = self._required_field(raw_item, path, field_name)
        if value is None:
            return 0
        if not self._is_int(value):
            self._add_issue(f"{path}.{field_name}", "Expected a positive integer")
            return 0
        if value <= 0:
            self._add_issue(f"{path}.{field_name}", "Expected a positive integer")
            return 0
        return value

    def _required_mapping(
        self, raw_item: Mapping[Any, Any], path: str, field_name: str
    ) -> Mapping[Any, Any]:
        value = self._required_field(raw_item, path, field_name)
        if value is None:
            return {}
        if not isinstance(value, Mapping):
            self._add_issue(f"{path}.{field_name}", "Expected a mapping")
            return {}
        return value

    def _optional_mapping(
        self, raw_item: Mapping[Any, Any], path: str, field_name: str
    ) -> dict[Any, Any]:
        if field_name not in raw_item:
            return {}

        value = raw_item[field_name]
        if not isinstance(value, Mapping):
            self._add_issue(f"{path}.{field_name}", "Expected a mapping")
            return {}

        return dict(value)

    def _required_field(self, raw_item: Mapping[Any, Any], path: str, field_name: str) -> Any:
        if field_name not in raw_item:
            self._add_issue(f"{path}.{field_name}", "Required field is missing")
            return None
        return raw_item[field_name]

    def _parse_port_key(self, raw_port: Any, path: str) -> int | None:
        if self._is_int(raw_port):
            port = raw_port
        elif isinstance(raw_port, str) and raw_port.isdecimal():
            port = int(raw_port)
        else:
            self._add_issue(path, f"Port key {raw_port!r} must be a positive integer")
            return None

        if port <= 0:
            self._add_issue(path, f"Port key {raw_port!r} must be a positive integer")
            return None
        return port

    def _check_allowed_fields(
        self,
        raw_item: Mapping[Any, Any],
        path: str,
        allowed_fields: set[str],
    ) -> None:
        for field_name in raw_item:
            if not isinstance(field_name, str):
                self._add_issue(path, f"Field name {field_name!r} must be a string")
            elif field_name not in allowed_fields:
                self._add_issue(f"{path}.{field_name}", f"Unknown field {field_name!r}")

    def _add_issue(self, path: str, message: str) -> None:
        self._issues.append(ConfigValidationIssue(path, message))

    def _raise_if_invalid(self) -> None:
        if self._issues:
            raise ConfigValidationError(self._issues)

    def _empty_config(self) -> WorkspaceFabricConfig:
        return WorkspaceFabricConfig(version=SCHEMA_VERSION)

    def _is_int(self, value: Any) -> bool:
        return isinstance(value, int) and not isinstance(value, bool)
