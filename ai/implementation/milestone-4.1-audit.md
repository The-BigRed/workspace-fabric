# Milestone 4.1 – Architecture and Audit

**Status:** Complete
**Date:** 2026-07-11
**Milestone:** Phase 4 – Modular Driver Platform

---

## Executive Summary

This audit establishes the baseline understanding of the current Workspace Fabric driver architecture before modularization. The analysis documents hard-coded driver registrations, vendor-specific dependencies in core code, package coupling, and configuration validation behavior. The audit provides a detailed migration order and temporary compatibility adapter strategy for Phase 4.2 and beyond.

**Key Finding:** ADR-0006 has been accepted. The current monolithic driver architecture can be modularized through entry-point discovery without rewriting working physical drivers.

---

## Acceptance Criteria – All Met

- ✅ The current implementation is understood before restructuring.
- ✅ No speculative rewrite is approved without evidence from the audit.
- ✅ The package and dependency targets are explicit.

---

## 1. Current Driver Architecture

### 1.1 Driver Registry and Factory

**Location:** `src/workspace_fabric/drivers/factory.py`

The current implementation uses a hard-coded dictionary registry:

```python
DRIVER_TYPES: dict[str, DriverFactory] = {
    driver_type: driver_class.from_config 
    for driver_type, driver_class in MOCK_DRIVER_TYPES.items()
} | {
    OreiUhd808VideoDriver.driver_type: OreiUhd808VideoDriver.from_config,
    OreiUkm404UsbDriver.driver_type: OreiUkm404UsbDriver.from_config,
}

def create_driver(config: DriverConfig) -> Driver:
    try:
        factory = DRIVER_TYPES[config.type]
    except KeyError as exc:
        supported = ", ".join(sorted(DRIVER_TYPES))
        raise ValueError(f"Unsupported driver type {config.type!r}; expected one of {supported}") from exc
    return factory(config)
```

**Implications:**
- Every driver must be imported at module load time.
- Drivers cannot be independently installed, upgraded, or removed.
- Adding or removing a driver requires modifying `factory.py`.
- No version negotiation between core and drivers.
- Unused vendor code cannot be cleanly removed from distributions.

### 1.2 Vendor-Specific Driver Implementations

| Driver | Type | Location | Dependencies | Status |
|--------|------|----------|--------------|--------|
| **Mock Video** | `mock_video_matrix` | `drivers/mock/video_matrix.py` | stdlib | Phase 3 |
| **Mock USB** | `mock_usb_matrix` | `drivers/mock/usb_matrix.py` | stdlib | Phase 3 |
| **OREI UHD-808** | `orei_uhd808` | `drivers/video/orei_uhd808.py` | socket, re | Phase 3 |
| **OREI UKM-404** | `orei_ukm404` | `drivers/usb/orei_ukm404.py` | socket, re | Phase 3 |

All drivers extend the base `Driver` class and implement:
- `from_config(config: DriverConfig) -> Driver`
- `driver_type` class variable
- `execute_action(plan: DriverActionPlan) -> DriverActionResult`
- `validate(config: WorkspaceFabricConfig) -> DriverValidationResult`
- `get_health() -> DriverHealth`
- `get_state() -> Mapping[str, Any]`

### 1.3 Mock Driver Registry

**Location:** `src/workspace_fabric/drivers/mock/factory.py`

```python
MOCK_DRIVER_TYPES = {
    MockVideoMatrixDriver.driver_type: MockVideoMatrixDriver,
    MockUsbMatrixDriver.driver_type: MockUsbMatrixDriver,
}
```

**Usage:** Mock detection in CLI (`src/workspace_fabric/cli/app.py`):
```python
replay_driver_ids = {
    config.id
    for config in self._config.drivers.values()
    if is_mock_driver_type(config.type)
}
```

This flag is used to replay mock driver state from transactions during CLI startup.

---

## 2. Vendor-Specific Dependencies in Core Code

### 2.1 Hard-Coded Imports in Driver Factory

**File:** `src/workspace_fabric/drivers/factory.py`

```python
from workspace_fabric.drivers.mock import MOCK_DRIVER_TYPES
from workspace_fabric.drivers.usb import OreiUkm404UsbDriver
from workspace_fabric.drivers.video import OreiUhd808VideoDriver
```

**Impact:**
- Core cannot be built or tested without vendor driver code present.
- Every driver import must be updated when drivers are packaged separately.
- No isolation between driver lifecycle and core initialization.

### 2.2 Hard-Coded Imports in Public API

**File:** `src/workspace_fabric/drivers/__init__.py`

```python
from workspace_fabric.drivers.factory import (
    DRIVER_TYPES,
    create_driver,
    create_drivers,
    is_mock_driver_type,
)
```

**Impact:**
- Consumers of the drivers module must transitively load all vendor drivers.
- Import-time side effects in drivers affect all downstream consumers.

### 2.3 Mock Driver Coupling in CLI

**File:** `src/workspace_fabric/cli/app.py`

```python
from workspace_fabric.drivers import is_mock_driver_type

# During state replay:
replay_driver_ids = {
    config.id
    for config in self._config.drivers.values()
    if is_mock_driver_type(config.type)
}
_replay_transactions(drivers, transactions, replay_driver_ids)
```

**Impact:**
- CLI cannot be built without mock driver code.
- Mock driver knowledge is baked into core orchestration logic.
- Once drivers are separately packaged, this will require a callback or driver capability interface.

---

## 3. Configuration and Validation Coupling

### 3.1 Configuration Model

**File:** `src/workspace_fabric/config/models.py`

```python
@dataclass
class DriverConfig:
    id: str
    type: str
    fabric: str
    connection: dict[str, Any] | None = None
    capabilities: dict[str, Any] | None = None
```

**Current Validation:** No driver-type validation at configuration load time. Validation is deferred to `create_driver()`.

### 3.2 Configuration Loader

**File:** `src/workspace_fabric/config/loader.py`

The loader parses YAML and constructs `DriverConfig` objects but does not validate driver types. This is correct – validation requires the runtime driver catalog to be populated.

### 3.3 Capability Validation

**File:** `src/workspace_fabric/core/capabilities/`

Capability validation occurs at resource-graph construction time and validates against driver capabilities. Once drivers are discovered dynamically, capability validation will need to incorporate driver type availability and version information.

---

## 4. Test Coupling

### 4.1 Driver Tests

| Test File | Coverage | Coupling |
|-----------|----------|----------|
| `tests/drivers/test_driver_factory.py` | Factory creates all driver types | Imports all driver classes |
| `tests/drivers/test_mock_drivers.py` | Mock driver behavior | Direct mock imports |
| `tests/drivers/test_orei_uhd808.py` | UHD-808 protocol and transport | Imports `OreiUhd808VideoDriver` |
| `tests/drivers/test_orei_ukm404.py` | UKM-404 protocol and transport | Imports `OreiUkm404UsbDriver` |
| `tests/drivers/test_driver_contract.py` | Base driver interface contract | Imports all driver types |

### 4.2 Integration Tests

| Test File | Drivers Used |
|-----------|--------------|
| `tests/test_smoke.py` | All drivers |
| `tests/physical/test_physical_smoke.py` | Hardware drivers (UHD-808, UKM-404) |
| `tests/config/test_loader.py` | Indirectly via configuration |
| `tests/core/test_resource_graph.py` | Mock drivers |

### 4.3 CLI Tests

**File:** `tests/cli/test_cli.py`

Tests exercise the full CLI with mock drivers. Once drivers are separately packaged, test configuration will need to ensure all necessary driver packages are installed.

---

## 5. Package Structure – Current State

```
src/workspace_fabric/
  drivers/
    base/           # Interfaces (portable)
      types.py
      __init__.py
    factory.py      # Hard-coded registry (will move to entry-point discovery)
    __init__.py     # Exports DRIVER_TYPES, create_driver, create_drivers
    mock/           # Mock implementations
      factory.py
      base.py
      video_matrix.py
      usb_matrix.py
      __init__.py
    video/          # OREI UHD-808 (vendor-specific)
      orei_uhd808.py
      __init__.py
    usb/            # OREI UKM-404 (vendor-specific)
      orei_ukm404.py
      __init__.py
    remote_console/ # (placeholder, empty)
      __init__.py
```

**Current Problem:** All drivers, base interfaces, and factory are in a single package. No boundary enforcement.

---

## 6. Migration Order and Compatibility Strategy

### Phase 4 Sequence (Detailed)

#### **Milestone 4.2 – Monorepo Package Structure**

**Step 1:** Create package directories
```
packages/
  core/              # Extract: config/, core/, cli/, api/
  driver-api/        # Extract: drivers/base/types.py → versioned Driver API
  driver-mock/       # Extract: drivers/mock/*
  driver-orei-uhd808/# Extract: drivers/video/orei_uhd808.py
  driver-orei-ukm404/# Extract: drivers/usb/orei_ukm404.py
```

**Step 2:** Update dependency direction
- `core` → `driver-api` (core reads driver contracts)
- `driver-*` → `driver-api` (drivers implement contracts)
- `driver-*` ↛ `core` (drivers never import core)

**Step 3:** Add root `pyproject.toml` for coordinated tooling

#### **Milestone 4.3 – Versioned Driver API**

**Step 1:** Stabilize and version `driver-api` package
- Extract: `Driver`, `DriverAction`, `DriverActionPlan`, `DriverActionResult`, `DriverActionStatus`, `DriverActionType`, `DriverCapabilityStatus`, `DriverHealth`, `DriverHealthStatus`, `DriverIssue`, `DriverIssueCategory`, `DriverObservedStateStatus`, `DriverValidationResult`
- Extract: capability and state models
- Define: `PluginDescriptor` with compatibility version
- Define: `ApiCompatibilityVersion` (independent of package version)

**Step 2:** Core and drivers depend on `driver-api`

#### **Milestone 4.4 – Installed-Driver Discovery**

**Step 1:** Update factory to use `importlib.metadata.entry_points()`

**Step 2:** Add entry points to `packages/driver-mock/pyproject.toml`:
```toml
[project.entry-points."workspace_fabric.drivers"]
mock_video_matrix = "workspace_fabric_driver_mock.plugin:get_plugin"
mock_usb_matrix = "workspace_fabric_driver_mock.plugin:get_plugin"
```

**Step 3:** Update factory discovery:
```python
def discover_drivers() -> dict[str, DriverFactory]:
    """Discover drivers via entry points."""
    discovered = {}
    for entry_point in importlib.metadata.entry_points(
        group="workspace_fabric.drivers"
    ):
        try:
            plugin = entry_point.load()
            driver_factory = plugin.get_driver_factory()
            discovered[entry_point.name] = driver_factory
        except Exception as e:
            # Log and isolate plugin-load failure
            pass
    return discovered
```

#### **Milestone 4.5 – Mock Driver Compatibility**

**Issue:** CLI imports `is_mock_driver_type()` to detect mock drivers for transaction replay.

**Solution – Temporary Compatibility Adapter:**
1. Each driver plugin declares metadata: `is_mock: bool`
2. Factory discovers this flag along with the driver
3. CLI queries discovered drivers for mock status instead of hard-coded list

**Later (Phase 5+):** Replace with capability-based detection (e.g., drivers expose `mock` capability).

---

## 7. Compatibility Adapters – Detailed Design

### 7.1 Mock Driver Detection

**Current Code (CLI):**
```python
replay_driver_ids = {
    config.id
    for config in self._config.drivers.values()
    if is_mock_driver_type(config.type)
}
```

**Adapter Strategy:**
1. In Milestone 4.4, add metadata to plugin descriptor
2. Factory maintains a registry of discovered drivers with their metadata
3. Replace `is_mock_driver_type(driver_type)` with `factory.is_mock_driver_type(driver_type)`

**Code Example (Phase 4.4+):**
```python
# In factory.py
class PluginDescriptor(NamedTuple):
    factory: DriverFactory
    is_mock: bool
    compatibility_version: str

DISCOVERED_DRIVERS: dict[str, PluginDescriptor] = {}

def discover_drivers() -> None:
    global DISCOVERED_DRIVERS
    # ... entry-point discovery ...
    DISCOVERED_DRIVERS = {driver_type: descriptor, ...}

def is_mock_driver_type(driver_type: str) -> bool:
    descriptor = DISCOVERED_DRIVERS.get(driver_type)
    return descriptor.is_mock if descriptor else False
```

### 7.2 Configuration Validation – Missing Driver

**Current Behavior:** `create_driver()` raises `ValueError` if driver type not found.

**Future Behavior (Phase 4.4+):** When creating drivers:
1. Check if driver type exists in discovered drivers
2. If not found and driver is configured, raise structured error:
   - Include driver type identifier
   - List available driver types
   - Suggest installing driver package

**Example:**
```python
class MissingDriverError(ConfigValidationError):
    def __init__(self, driver_type: str, available_types: list[str]):
        self.driver_type = driver_type
        self.available_types = available_types
        super().__init__(
            f"Driver '{driver_type}' not found. "
            f"Available: {', '.join(available_types)}. "
            f"Install with: pip install workspace-fabric-driver-{driver_type}"
        )
```

### 7.3 Driver API Compatibility

**During Phase 4.3:**
1. Each driver plugin declares Driver API version it supports
2. Core declares Driver API version(s) it accepts
3. Factory validates compatibility before loading driver

**Example:**
```python
class PluginDescriptor:
    def __init__(self, entry_point, factory, metadata):
        self.factory = factory
        self.driver_api_version = metadata.get("driver_api_version", "1.0")
        self.is_mock = metadata.get("is_mock", False)
```

---

## 8. Identified Vendor-Specific Code

### 8.1 In Core (to be removed)

| Location | Dependency | Action |
|----------|----------|--------|
| `drivers/factory.py` | Direct import of `OreiUhd808VideoDriver` | Move to entry point |
| `drivers/factory.py` | Direct import of `OreiUkm404UsbDriver` | Move to entry point |
| `drivers/__init__.py` | Re-export of all drivers | Update to dynamic discovery |
| `cli/app.py` | Import of `is_mock_driver_type` | Replace with query function |
| `config/loader.py` | Parse driver configs | No change needed |

### 8.2 In Drivers (to remain, now in separate packages)

**OREI UHD-808:**
- `socket` module usage (vendor protocol)
- Telnet-style command protocol
- HDMI port mapping logic
- Route parsing

**OREI UKM-404:**
- `socket` module usage (vendor protocol)
- USB matrix protocol
- Device-to-host routing logic

**Mock Drivers:**
- In-memory state tracking
- Transaction replay
- No external dependencies

---

## 9. Configuration Stability

### 9.1 YAML Configuration – No Breaking Changes

Current supported configuration:
```yaml
version: 1
drivers:
  uhd808:
    type: orei_uhd808
    fabric: physical_lab
    connection:
      transport: telnet
      host: 172.24.2.192
      port: 23
  ukm404:
    type: orei_ukm404
    fabric: physical_lab
    connection:
      transport: telnet
      host: 172.24.2.193
      port: 23
```

**Stability Commitment:** Driver type identifiers remain unchanged:
- `mock_video_matrix` ✅
- `mock_usb_matrix` ✅
- `orei_uhd808` ✅
- `orei_ukm404` ✅

Configuration validation will be **more strict** once drivers are packaged (missing drivers will fail validation), but **no existing valid configurations will break**.

---

## 10. Summary of Phase 4.1 Findings

| Finding | Impact | Mitigation |
|---------|--------|-----------|
| Hard-coded driver registry | Cannot install drivers independently | Replace with entry-point discovery (4.4) |
| Vendor imports in core | Core coupled to vendor code | Extract drivers to separate packages (4.2) |
| No driver versioning | Drivers tied to core releases | Implement semantic versioning per package (4.3) |
| Mock detection hard-coded in CLI | Mock drivers are special-case | Add driver metadata; query at runtime (4.4) |
| No entry points defined | Cannot discover installed drivers | Add entry points to driver packages (4.4) |
| Single package | No boundary enforcement | Restructure into monorepo packages (4.2) |

---

## 11. Acceptance Sign-Off

- ✅ ADR-0006 (Modular Driver Packaging and Discovery) is accepted and used as the basis for this audit.
- ✅ All current driver registrations, factories, and imports are documented.
- ✅ All vendor-specific dependencies in core code are identified with locations and impact.
- ✅ Package and test coupling is documented with examples.
- ✅ Migration order is explicit: 4.2 → 4.3 → 4.4 → 4.5.
- ✅ Temporary compatibility adapters are designed for smooth transition.

**This audit is complete. Phase 4.2 can proceed with monorepo restructuring.**

---

## Appendix A: Files Changed During Phase 4

### Phase 4.2 (Monorepo Structure)
- [ ] Create `packages/core/pyproject.toml`
- [ ] Create `packages/driver-api/pyproject.toml`
- [ ] Create `packages/driver-mock/pyproject.toml`
- [ ] Create `packages/driver-orei-uhd808/pyproject.toml`
- [ ] Create `packages/driver-orei-ukm404/pyproject.toml`
- [ ] Move `src/workspace_fabric/{config,core,cli,api}` → `packages/core/src/`
- [ ] Move `src/workspace_fabric/drivers/base/types.py` → `packages/driver-api/src/`
- [ ] Move `src/workspace_fabric/drivers/mock/*` → `packages/driver-mock/src/`
- [ ] Move `src/workspace_fabric/drivers/video/*` → `packages/driver-orei-uhd808/src/`
- [ ] Move `src/workspace_fabric/drivers/usb/*` → `packages/driver-orei-ukm404/src/`
- [ ] Create root `pyproject.toml` with development dependencies

### Phase 4.3 (Driver API)
- [ ] Extract `DriverPlugin`, `PluginDescriptor`, `ApiCompatibilityVersion`
- [ ] Update core `pyproject.toml` to depend on `driver-api`
- [ ] Update driver `pyproject.toml` files to depend on `driver-api`

### Phase 4.4 (Entry Points)
- [ ] Add `[project.entry-points]` to driver `pyproject.toml` files
- [ ] Update `factory.py` to use `importlib.metadata.entry_points()`
- [ ] Update `DRIVER_TYPES` discovery logic
- [ ] Add plugin metadata for mock driver detection

### Phase 4.5 (CLI Compatibility)
- [ ] Update CLI to query factory for mock driver types
- [ ] Update transaction replay logic

---

**Document Version:** 1.0
**Status:** Complete
**Next Step:** Phase 4.2 – Monorepo Package Structure
