# Repository Skeleton

## Purpose

This document defines the initial repository structure for Workspace Fabric.

The skeleton should separate core orchestration, drivers, agents, APIs, tests, examples, and AI guidance from the beginning.

## Proposed Structure

```text
workspace-fabric/
  README.md
  LICENSE
  docs/
    architecture.md
    vision.md
    glossary.md
    resource-model.md
    capability-model.md
    driver-contract.md
    transaction-model.md
    configuration-model.md
    phase-2-foundation.md
    repository-skeleton.md
    hardware/
      orei-uhd808.md
      orei-ukm404.md
    design/
      architecture-capture-2026-07.md
    adr/
  examples/
    local-workspace.yaml
  src/
    workspace_fabric/
      __init__.py
      api/
      cli/
      config/
      core/
        resources/
        graph/
        planner/
        transactions/
        state/
      drivers/
        base/
        mock/
        video/
        usb/
        remote_console/
      integrations/
  tests/
    config/
    core/
    drivers/
    transactions/
  .ai/
    project.md
    architecture-summary.md
    coding-guidelines.md
    implementation-roadmap.md
```

## Notes on Language

This skeleton uses a Python-style structure because Python is well suited for early hardware integration, serial/TCP experimentation, and rapid iteration.

If the project later moves to Go, the conceptual structure should remain similar:

```text
cmd/
internal/
pkg/
docs/
examples/
.ai/
```

The architecture should not depend on the implementation language.

## Core Folder

`src/workspace_fabric/core/` contains vendor-independent orchestration logic.

It should include:

- Resource graph.
- Route validation.
- Capability validation.
- Transaction planning.
- Transaction execution.
- State management.

It must not include OREI, PiKVM, Windows, or other vendor-specific protocol code.

## Driver Folder

`src/workspace_fabric/drivers/` contains driver interfaces and implementations.

Recommended layout:

```text
drivers/
  base/
    interfaces.py
    capabilities.py
    errors.py
  mock/
    video_matrix.py
    usb_matrix.py
    remote_console.py
  video/
    orei_uhd808.py
  usb/
    orei_ukm404.py
  remote_console/
    pikvm.py
```

Real drivers should not be implemented until mock drivers and the driver contract are stable.

## API Folder

`api/` should expose the control plane.

V0 may skip API implementation if CLI is easier, but the architecture remains API-first.

## CLI Folder

`cli/` provides early usability and development commands.

The CLI should call the same core services that the API will eventually call.

## Agents

Agents such as the future Windows Display Agent should live outside the core controller unless implemented as separate packages.

Possible future structure:

```text
agents/
  windows-display-agent/
  linux-display-agent/
```

## Examples

Examples are important because AI tools will use them as patterns.

Include a working mock example early:

```text
examples/local-workspace.yaml
```

## AI Folder

`.ai/` contains AI-specific guidance.

These files should be concise, authoritative, and repeatedly referenced by Codex/OpenClaw.

They are not a substitute for docs. They are onboarding summaries and guardrails.
