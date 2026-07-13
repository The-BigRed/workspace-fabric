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
