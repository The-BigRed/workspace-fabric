# Workspace Fabric Backlog

## Purpose

The Workspace Fabric Backlog contains work that has been accepted for future
implementation.

Unlike the Architectural Considerations document, items in the backlog represent
project commitments. While implementation order may change, backlog items are
expected to be completed as development priorities and available resources
permit.

The backlog is intentionally organized by product area rather than release or
priority. Priority and planning horizon are tracked as attributes of each item.

---

# Relationship to Other Planning Documents

The planning documents serve different purposes.

| Document | Purpose |
|----------|---------|
| Roadmap | Defines the path to the next major project milestone. |
| Architectural Considerations | Records ideas and capabilities the architecture should remain prepared to support. |
| Backlog | Tracks accepted work that the project intends to implement. |
| Release Strategy | Defines how software is versioned and released. |
| CHANGELOG | Records completed work. |

---

# Workflow

Accepted work generally progresses through the following lifecycle.

```text
Architectural Considerations
        │
        ▼
Backlog
        │
        ▼
Implementation
        │
        ▼
CHANGELOG
```

Not every architectural consideration becomes a backlog item.

Items are promoted only after there is demonstrated operational value or a
clear project need.

---

# Planning Horizons

Planning Horizon describes *when* the project expects to address an item.

## Now

Actively planned work expected during the current development cycle.

## Next

Accepted work expected after the current effort completes.

## Later

Accepted work without a scheduled implementation target.

Planning Horizon is intentionally independent of Priority.

---

# Priority Definitions

## High

Significant impact on usability, stability, or project goals.

## Medium

Important improvements that enhance the platform but are not immediately
required.

## Low

Useful enhancements that may be implemented when time and demand justify the
investment.

---

# Core Platform

## API Key Management

**Status**

Accepted

**Planning Horizon**

Now

**Priority**

High

**Description**

Implement API key lifecycle management, including creation, revocation,
rotation, and metadata.

Support Workspace Fabric's OAuth-style permission scopes defined by ADR-0007.

**Notes**

The initial administrative API key is intentionally created during installation
or by trusted local CLI access.

---

## Windows Display Agent

**Status**

Accepted

**Planning Horizon**

Next

**Priority**

High

**Description**

Implement the Windows Display Agent responsible for operating-system display
management that cannot be performed through external display hardware alone.

Initial capabilities include:

- Enable and disable displays
- Primary display selection
- Display arrangement support where practical
- Display state synchronization
- Integration with Workspace Fabric transactions

**Motivation**

Reference hardware validation demonstrated that modern HDMI matrices may
maintain Hot Plug Detect (HPD) even when outputs are unrouted.

The Windows Display Agent provides the operating-system functionality required
to produce the intended workspace behavior despite hardware limitations.

---

## Workspace Awareness

**Status**

Accepted

**Planning Horizon**

Next

**Priority**

High

**Description**

Expose the effective operational state of the Workspace Fabric control plane.

Examples include:

- Active workspaces
- Active scenes
- Applied patches
- Effective routing
- Controller state
- Transaction status
- Desired versus current state

**Motivation**

Workspace Awareness provides the information required by user interfaces,
automation platforms, diagnostics, and AI agents to understand the current
state of the fabric without reconstructing it independently.

---

## Transaction History

**Status**

Accepted

**Planning Horizon**

Next

**Priority**

Medium

**Description**

Persist transaction history to simplify troubleshooting, auditing, and future
diagnostic capabilities.

---

## Configuration Migration

**Status**

Accepted

**Planning Horizon**

Next

**Priority**

Medium

**Description**

Provide automatic migration of configuration files between supported schema
versions.

---

# Drivers

## UHD-808 Advanced Capabilities

**Status**

Accepted

**Planning Horizon**

Next

**Priority**

High

**Description**

Expand the UHD-808 driver to expose advanced hardware capabilities including:

- EDID management
- Output scaling
- CEC control
- Enhanced routing diagnostics

**Motivation**

The reference hardware already supports these capabilities and they
significantly improve the value of the reference implementation.

---

## Additional Matrix Drivers

**Status**

Accepted

**Planning Horizon**

Later

**Priority**

Medium

**Description**

Implement support for additional HDMI and USB matrix hardware while preserving
the generic driver contract.

---

## Additional Platform Drivers

**Status**

Accepted

**Planning Horizon**

Later

**Priority**

Medium

**Description**

Expand support for additional device classes including:

- Audio DSPs
- PDUs
- BMCs
- KVMs
- Display controllers
- Operating system agents

---

# User Experience

## Topology Visualization

**Status**

Accepted

**Planning Horizon**

Next

**Priority**

High

**Description**

Provide graphical visualization of the current fabric, including devices,
controllers, endpoints, routes, and active workspaces.

---

## Configuration Templates

**Status**

Accepted

**Planning Horizon**

Later

**Priority**

Medium

**Description**

Allow reusable templates for common hardware layouts and workspace
configurations.

---

## Improved Diagnostics

**Status**

Accepted

**Planning Horizon**

Next

**Priority**

Medium

**Description**

Expand diagnostic tooling to simplify troubleshooting and hardware validation.

Examples include:

- Driver health
- Capability validation
- Route validation
- Controller connectivity
- Configuration validation

---

# Developer Experience

## Driver Development Toolkit

**Status**

Accepted

**Planning Horizon**

Later

**Priority**

Medium

**Description**

Provide utilities that simplify development, validation, and testing of new
drivers.

---

## Enhanced Driver Discovery

**Status**

Accepted

**Planning Horizon**

Later

**Priority**

Medium

**Description**

Expand driver metadata and discovery capabilities to improve automatic
configuration and future UI experiences.

---

# Documentation

## Operator Documentation

**Status**

Accepted

**Planning Horizon**

Next

**Priority**

Medium

**Description**

Develop comprehensive operator documentation covering installation,
configuration, troubleshooting, and day-to-day operation.

---

## Driver Author Guide

**Status**

Accepted

**Planning Horizon**

Later

**Priority**

Medium

**Description**

Produce a complete guide for implementing Workspace Fabric drivers using the
published driver contract.

---

# Maintenance

Completed work should be removed from the backlog and recorded in
`CHANGELOG.md`.

Items that require architectural changes should reference the appropriate ADR
before implementation begins.

Priority and Planning Horizon should be reviewed periodically to ensure they
continue to reflect the project's current direction.

---

# Guiding Principle

The backlog represents the project's current implementation commitments.

Items should be added deliberately, remain appropriately scoped, and reflect
demonstrated value rather than speculative functionality.

Maintaining a focused backlog helps ensure that Workspace Fabric continues to
evolve in a predictable, maintainable, and architecturally consistent manner.
