# Phase 3: Hardware Integration

## Status

Complete

## Purpose

Validate the Workspace Fabric architecture against physical HDMI and USB matrix
hardware while preserving the core/driver boundary.

## Milestones

### 3.1 Driver Contract Hardening ✅

- Confirmed common driver interfaces
- Documented required methods
- Added capability, state, and structured-error expectations

### 3.2 OREI UHD-808 Video Driver ✅

- Implemented Telnet-style command transport
- Implemented video route application
- Implemented route-state query and parsing
- Added mocked transport tests
- Validated against physical hardware

### 3.3 OREI UKM404 USB Driver ✅

- Implemented USB device-to-host routing
- Implemented route-state query
- Added mocked transport tests
- Validated against physical hardware

### 3.4 Physical Lab Configuration ✅

- Created `examples/physical-local.yaml`
- Mapped physical video sources and outputs
- Mapped USB devices and per-matrix host ports
- Validated the installed reference topology

### 3.5 End-to-End Physical Smoke Test ✅

- Applied `desktop`
- Applied `work`
- Applied `hybrid_meeting`
- Confirmed physical video and USB switching
- Confirmed observed route state

### 3.6 Safety and Recovery ✅

- Documented dry-run-first operation
- Added timeout and connection-failure handling
- Added structured hardware-rejection and state-query behavior
- Documented retry, recovery, and manual fallback expectations

## Completion Criteria

Phase 3 is complete because:

- Physical configuration validates.
- The core resolves logical resources to controller-local ports.
- The CLI plans and applies real hardware changes.
- UHD-808 and UKM404 drivers operate through the common contract.
- Observed state is reported where supported.
- Unknown state remains explicit.
- Partial failures are represented honestly.
- The full physical smoke sequence passes.

## Release

Phase 3 establishes the `v0.3.0` physically validated baseline.

Further driver packaging work belongs to Phase 4. Product APIs and applications
belong to Phase 5. New hardware capabilities and integrations belong to Phase 6.
