
# Workspace Fabric Driver API Guidance

## Purpose
This document provides implementation guidance for contributors and AI agents implementing Workspace Fabric drivers.

Authoritative references remain:
- docs/architecture.md
- docs/driver-contract.md
- ADRs
- capability-model.md
- configuration-model.md

## Core Principles
- Drivers are independently installable packages.
- Drivers are independently versioned.
- The core remains vendor-neutral.
- The core communicates only through the published Driver API.
- Vendor protocols, parsing, retries, framing, and quirks belong inside drivers.
- Driver discovery uses Python entry points.
- Missing drivers produce structured validation errors.
- Drivers report observed state honestly.

## Intended Package Layout

```text
packages/
  core/
  driver-api/
  driver-mock/
  driver-orei-uhd808/
  driver-orei-ukm404/
```

## Dependency Rules

Allowed:
- core -> driver-api
- driver -> driver-api

Disallowed:
- core -> vendor driver
- driver-api -> core
- driver -> core internals

## Plugin Metadata
Each driver should expose:
- driver type
- display name
- driver version
- supported Driver API version
- factory
- configuration metadata
- capability metadata
- port metadata

## Responsibilities
Drivers:
- validate configuration
- connect to hardware
- execute assigned actions
- normalize protocol responses
- report observed state
- return structured results

Drivers do not:
- interpret workspaces
- perform global planning
- coordinate other drivers
- implement global policy

## Phase 4 Goal
Establish a modular driver platform without changing validated hardware behavior. Existing drivers should migrate into independently installable packages while preserving backward compatibility.
