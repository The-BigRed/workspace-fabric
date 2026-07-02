# ADR 0001: Use Python as the primary project language

## Status

Accepted

## Context

Workspace Fabric needs to control physical hardware, expose APIs, support automation, and remain approachable for AI-assisted development.

## Decision

Workspace Fabric will use Python as the primary implementation language.

## Rationale

Python has strong support for network automation, serial communication, REST APIs, async I/O, configuration formats, and rapid prototyping. It is also well-supported by AI coding tools and has a large ecosystem.

## Consequences

Python will be used for the initial control plane, hardware drivers, CLI, and API service. Future components may use other languages when justified, but Python is the default unless an ADR records a different decision.
