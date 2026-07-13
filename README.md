# Workspace Fabric

> **Workspace Fabric makes complex workspaces behave like software.**

Modern desks, labs, studios, and control rooms often contain multiple
computers, displays, USB peripherals, KVMs, video matrices, remote consoles,
and automation systems. Changing from one workflow to another frequently
requires manually switching cables, changing monitor inputs, moving USB
devices, launching remote consoles, and coordinating multiple independent
systems.

Workspace Fabric replaces those manual steps with a single software-defined
model. Instead of telling individual devices what to do, users describe the
workspace they want, and Workspace Fabric determines the hardware and software
actions required to make it happen.

Whether switching from a desktop to a work laptop, preparing a hybrid meeting,
connecting to a server through an IP-KVM, or coordinating an entire AV
environment, Workspace Fabric provides a deterministic control plane that
translates user intent into reproducible operations.

Workspace Fabric is designed to scale naturally from a single desk with two
computers and a pair of monitors to complex multi-user environments while
presenting the same consistent programming model to users, automation systems,
and future AI agents.

---

# At a Glance

- Hardware-independent architecture
- API-first design
- Deterministic transaction engine
- Modular driver platform
- Interactive configuration (planned)
- Optional Reference Web UI
- Automation and AI friendly

---

# A Practical Example

Imagine you're deploying a software update to a production environment.

The deployment has entered a database migration that's expected to take nearly
an hour. You need to monitor its progress, but there's nothing to do while it
runs.

Rather than dedicating your entire workstation to watching a progress bar, you
simply activate your **Hybrid Work** workspace.

Within seconds:

- Your primary monitor continues displaying the deployment.
- Your secondary monitor switches to your personal desktop.
- Your keyboard, mouse, and speakers follow the secondary workspace.
- Your deployment continues uninterrupted.
- Monitoring and notifications remain active.
- Returning to your full work environment later is a single workspace change
  away.

A few minutes later, the deployment requires attention.

Rather than leaving the Hybrid Work workspace, you simply apply the
**Primary Input** patch.

Your keyboard and mouse immediately return to the work system while both
monitors remain exactly where they are.

After addressing the issue, applying the **Secondary Input** patch returns your
keyboard and mouse to the secondary workspace without interrupting either
display.

Traditional KVMs and matrix switches expose hardware operations.

Workspace Fabric exposes reusable **workspaces** and targeted **patches** that
describe **what** should change rather than **how** it should change.

The operator never thinks about HDMI ports, USB matrices, monitor inputs, or
remote consoles.

They simply select the workspace they need, and Workspace Fabric determines how
to create it.

---

# What Makes Workspace Fabric Different?

Workspace Fabric is not a KVM.

It is not a matrix controller.

It is not a remote desktop launcher.

It is not an automation platform.

It is the software-defined control plane consumed by those systems.

Unlike traditional KVM software or vendor-specific matrix controllers,
Workspace Fabric is hardware independent.

Drivers isolate vendor-specific behavior, allowing the same workspace model to
operate across different hardware while exposing a stable API for user
interfaces, automation systems, and AI agents.

The long-term goal is simple:

> **Users should think about the workspace they want—not the hardware required
> to create it.**

---

# Architecture Overview

Workspace Fabric models physical and virtual resources independently before
assembling them into reusable operating environments.

```text
Driver
    ↓
Controller
    ↓
Resources
    ↓
Workspace
    ↓
Scene
    ↓
Patch
```

The core validates requested changes, plans deterministic transactions, and
coordinates vendor-specific drivers to safely transition the environment from
its current state to the desired workspace.

Drivers remain responsible only for translating generic Workspace Fabric
actions into native hardware or software operations.

---

# Current Status

Workspace Fabric has completed:

**Phase 4 – Modular Driver Platform**

The current development phase is:

**Phase 5 – Relationship-Oriented Control Plane**

Completed:

- ✅ Architecture
- ✅ Foundation
- ✅ Hardware Integration
- ✅ Modular Driver Platform

Current and planned:

- Phase 5 – Relationship-Oriented Control Plane
- Phase 6 – Core Interfaces
- Phase 7 – Configuration Experience
- Phase 8 – Productization
- Release 1.0

Detailed project status is maintained in
[`PROJECT_STATUS.md`](PROJECT_STATUS.md).

---

# Repository Guide

| Document | Purpose |
|----------|---------|
| `docs/architecture.md` | High-level system architecture |
| `docs/philosophy.md` | Long-term engineering philosophy |
| `docs/roadmap.md` | Development roadmap toward Release 1.0 |
| `PROJECT_STATUS.md` | Current implementation status |
| `CHANGELOG.md` | Project history |
| `docs/architecture/adr/` | Architectural Decision Records |
| `docs/planning/` | Planning, backlog, release strategy, and architectural considerations |

---

# Getting Started

Current development focuses on the reference implementation.

Developers interested in contributing should begin by reading:

1. `docs/philosophy.md`
2. `docs/architecture.md`
3. The Architectural Decision Records
4. `docs/roadmap.md`
5. `PROJECT_STATUS.md`

Together these documents explain both the architecture and the current
development priorities.

---

# Development Principles

Workspace Fabric is intentionally built around several enduring principles.

- Intent over implementation
- Hardware-independent architecture
- Deterministic execution
- API-first design
- Stable architectural boundaries
- Progressive capability
- Composition over specialization

These principles guide every architectural and implementation decision.

---

# Project Planning

During initial development, Workspace Fabric follows a milestone-driven
roadmap.

Following Release 1.0, development transitions to release-based planning.

Future work is tracked through:

- Backlog
- Architectural Considerations
- Release Strategy
- CHANGELOG

rather than additional numbered development phases.

---

# Contributing

Contributors are encouraged to understand the architecture before implementing
new functionality.

Significant architectural changes should be documented through an
Architectural Decision Record (ADR).

The project favors architectural stability, deterministic behavior, and
maintainable abstractions over rapid feature growth.

---

# License

*License to be determined.*
