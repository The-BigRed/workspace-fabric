# Workspace Fabric Roadmap

## Purpose

This document describes the planned evolution of Workspace Fabric through its
first complete public release.

Detailed implementation progress is tracked in `PROJECT_STATUS.md`.

After the initial public release, development transitions from milestone-driven
planning to release-based development. Future work is tracked through the
project planning documents rather than additional numbered phases.

---

# Phase 1 - Architecture - Complete

## Objective

Define the core architecture, engineering philosophy, terminology, and
architectural boundaries.

## Outcome

A stable architectural foundation capable of supporting multiple hardware
platforms without coupling the core to vendor-specific implementations.

---

# Phase 2 - Foundation - Complete

## Objective

Build the hardware-independent core platform.

## Major Deliverables

- Repository structure
- Configuration loader
- Resource graph
- Capability validation
- Transaction planner
- Transaction executor
- Mock drivers
- Persistent state
- Initial CLI

## Outcome

Workspace Fabric can validate configuration, plan transactions, and execute
operations against mock hardware.

---

# Phase 3 - Hardware Integration - Complete

## Objective

Validate the architecture against real HDMI and USB matrix hardware.

## Major Deliverables

- Driver contract hardening
- Physical lab configuration
- OREI UHD-808 driver
- OREI UKM404 driver
- End-to-end physical validation
- Safety and recovery behavior

## Outcome

Workspace Fabric successfully transitioned from mock drivers to physical
hardware. The driver abstraction, controller model, transaction engine, and
configuration architecture were validated against the reference environment.

Windows Display Agent and PiKVM-specific implementations remain future work.

---

# Phase 4 - Modular Driver Platform - Complete

## Objective

Decouple drivers from the Workspace Fabric core and establish a modular,
independently versioned driver platform.

## Major Deliverables

- Driver package architecture
- Versioned Driver API
- Plugin discovery
- Driver metadata catalog
- Independent driver lifecycle
- Mock driver migration
- OREI driver migration
- Physical regression validation

## Outcome

Drivers are independently installable, discoverable, versioned, and validated.

The Workspace Fabric core contains no vendor-specific implementations and
interacts with drivers through the published Driver API and entry-point
metadata.

---

# Phase 5 - Relationship-Oriented Control Plane - Current

## Objective

Implement the relationship-oriented orchestration model defined by ADR-0005 and
ADR-0009.

## Major Deliverables

- Endpoint metadata
- Endpoint constraints
- Relationship model
- Relationship planner
- Relationship groups
- Managed scope reconciliation
- Structured supported, unsupported, and unknown outcomes
- Mock-first driver metadata updates
- Physical regression validation

## Completion Criteria

The core can reason about endpoint relationships, cardinality, reconciliation,
and constraints while drivers remain descriptive and existing validated
physical behavior remains operational.

---

# Phase 6 - Core Interfaces

## Objective

Expose the Workspace Fabric control plane through stable public interfaces.

## Major Deliverables

- Stable REST API
- API versioning
- API documentation
- Administrative CLI
- Public CLI
- Transaction APIs
- State APIs
- Workspace, Scene, Patch, and relationship APIs
- Health APIs
- API key authentication and authorization scopes

## Completion Criteria

Every core Workspace Fabric operation is available through documented public
interfaces without requiring consumers to know internal implementation details.

---

# Phase 7 - Configuration Experience

## Objective

Replace manual configuration authoring with an intuitive interactive
configuration experience.

## Major Deliverables

- Driver onboarding
- Interactive configuration
- Physical topology editor
- Workspace editor
- Scene editor
- Patch editor
- Configuration validation
- Reference Web UI
- Desktop application evaluation

## Completion Criteria

Users can configure and operate Workspace Fabric without manually editing YAML.
YAML remains the serialized source of truth rather than the primary authoring
experience.

---

# Phase 8 - Productization

## Objective

Deliver the first complete public release of Workspace Fabric.

## Major Deliverables

- Packaging
- Installation
- API key lifecycle management
- Diagnostics
- Logging
- Backup and restore
- Configuration migration
- Operator documentation
- Stable public API (v1)
- Release readiness validation

## Completion Criteria

Workspace Fabric is suitable for daily production use. Installation,
configuration, operation, and maintenance are documented and validated.

---

# Release 1.0

Completion of Phase 8 constitutes the first complete public release of
Workspace Fabric.

Subsequent development is managed through:

- Project Backlog
- Architectural Considerations
- Release Strategy
- CHANGELOG

rather than additional numbered phases.

Future enhancements are intentionally managed independently of the initial
development roadmap.
