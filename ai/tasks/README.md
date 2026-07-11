# AI Task Library

## Purpose

The `ai/tasks/` directory contains reusable workflows for AI coding
agents working on Workspace Fabric.

Unlike the files in `docs/`, these task documents describe **how** to
perform common engineering activities. They are intended to reduce
prompt size, encourage consistent implementation practices, and capture
proven development workflows as the project evolves.

## How to Use

When requesting work from an AI coding agent:

1.  Reference the appropriate task document.
2.  Identify the target device or subsystem.
3.  Describe the desired outcome or milestone.
4.  Allow the task document to provide the implementation process.

Example:

> Read `ai/tasks/hardware-driver-implementation.md` and implement the
> next milestone for `docs/hardware/orei-uhd-808`.

## Available Tasks

  ---------------------------------------------------------------------------------------
  Task                                         Purpose
  -------------------------------------------- ------------------------------------------
  `hardware-command-reference-extraction.md`   Extract a vendor manual into a
                                               development-friendly command reference.

  `hardware-driver-implementation.md`          Implement or extend a hardware driver
                                               while following the documented
                                               architecture, driver contract, and
                                               engineering standards.

  `hardware-driver-documentation.md`           Keep driver documentation synchronized
                                               with implementation and verified hardware
                                               behavior.
  ---------------------------------------------------------------------------------------

## Guiding Principles

-   Tasks describe repeatable engineering processes.
-   Tasks are hardware-agnostic unless explicitly stated otherwise.
-   Prefer extending an existing task over creating duplicate workflows.
-   Improve task documents when a better repeatable process is
    discovered.
-   Keep project architecture in `docs/`; keep implementation workflows
    in `ai/tasks/`.

## Adding New Tasks

Create a new task only when the process is expected to be reused across
multiple devices, milestones, or contributors.

Potential future tasks include:

-   Hardware driver testing
-   Hardware validation
-   Architecture document updates
-   ADR creation
-   Release preparation

New tasks should focus on reusable engineering practices rather than
project-specific decisions.
