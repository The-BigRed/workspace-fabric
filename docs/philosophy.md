# Workspace Fabric Philosophy

## Purpose

This document captures the enduring engineering philosophy behind Workspace Fabric. It complements the Vision and Architecture documents by recording the principles used to evaluate future design decisions.

## Guiding Principles

- **Intent Over Implementation** — Users describe the workspace they want, not hardware commands.
- **Resources Over Devices** — The core models logical resources; hardware realizes them.
- **Explicit Over Implicit** — Model relationships explicitly rather than inferring topology.
- **Composition Over Specialization** — Extend the model through composition instead of creating special cases.
- **Hardware Independence** — Reference hardware validates the design but never defines the architecture.
- **Progressive Capability** — Advanced hardware enriches the experience without penalizing simpler hardware.
- **Transactions Over Commands** — Workspace changes are validated, planned, executed, and verified.
- **Software-Defined Workspace** — Resources may be physical, virtual, local, or remote.
- **Build for Evolution** — Solve today's problems without preventing tomorrow's capabilities.

## Design Litmus Test

Before implementing a feature, ask:

1. Does this help users compose a workspace rather than manipulate hardware?
2. Does it belong in the core or in a driver?
3. Does it strengthen the resource model?
4. Would it still make sense if the underlying hardware changed?

## Philosophy Statement

> Workspace Fabric is a control plane that weaves independent workspace resources into a coherent, programmable operating environment.
