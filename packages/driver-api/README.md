# Workspace Fabric Driver API

This package contains the portable contracts shared by Workspace Fabric core
code and independently installable driver packages.

It intentionally imports neither core orchestration modules nor vendor driver
implementations.

## Compatibility Version

`DRIVER_API_COMPATIBILITY_VERSION` is the Driver API contract version. It is
independent from this package's release version and from every driver package
version.

Compatibility follows semantic-version major/minor rules:

- Same major version is required.
- A driver declaring an older or equal minor version is compatible.
- A driver requiring a newer minor version is rejected before construction.
- A different major version is rejected before construction.

Driver packages declare compatibility through `PluginDescriptor`:

```python
from workspace_fabric_driver_api import (
    DRIVER_API_COMPATIBILITY_VERSION,
    PluginDescriptor,
)


def get_plugin_descriptor() -> PluginDescriptor:
    return PluginDescriptor(
        driver_type="example_driver",
        display_name="Example Driver",
        driver_version="1.0.0",
        supported_driver_api=DRIVER_API_COMPATIBILITY_VERSION,
        factory=ExampleDriver.from_config,
)
```

## Driver Metadata

Driver descriptors should also include metadata that future onboarding and
configuration surfaces can consume without importing vendor-specific code:

- `configuration_schema`
- `port_metadata`
- `capability_metadata`
- `package_name`
- `is_mock`

The `factory` remains part of the descriptor for controller construction, but
catalog projections should expose only serializable metadata to public APIs.

## Entry-Point Registration

Driver packages register one entry point per driver type under
`workspace_fabric.drivers`:

```toml
[project.entry-points."workspace_fabric.drivers"]
example_driver = "workspace_fabric_driver_example.plugin:get_plugin_descriptor"
```

The core discovers installed packages through `importlib.metadata.entry_points`.
Production discovery must not scan arbitrary source folders.

## Discovery Diagnostics

The core discovery layer reports these structured categories:

- `missing_driver`
- `duplicate_driver_type`
- `incompatible_driver_api`
- `plugin_load_failed`

A broken entry point is isolated and reported as `plugin_load_failed`; unrelated
compatible driver plugins remain discoverable.
