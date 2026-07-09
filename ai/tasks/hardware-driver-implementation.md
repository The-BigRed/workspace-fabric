# Hardware Driver Implementation Task

## Purpose

Implement or extend a Workspace Fabric hardware driver using the
project's documented architecture and engineering standards.

## Read First

Before making code changes, read:

1.  AGENTS.md
2.  PROJECT_STATUS.md
3.  docs/phase-3-hardware-drivers.md (or current phase document)
4.  docs/driver-contract.md
5.  docs/reference-platform.md
6.  docs/hardware/`<device>`{=html}/driver.md
7.  docs/hardware/`<device>`{=html}/protocol-notes.md
8.  docs/hardware/`<device>`{=html}/observations.md
9.  Vendor manual(s)

## Workflow

1.  Identify the current milestone and confirm the task fits that
    milestone.
2.  Review the driver contract before writing code.
3.  Compare vendor capabilities with the Workspace Fabric capability
    model.
4.  Scaffold only the functionality needed for the requested feature.
5.  Implement incrementally.
6.  Keep the core hardware-agnostic.
7.  Do not invent undocumented protocol behavior.
8.  Return structured errors for unsupported or unknown operations.
9.  Add or update unit tests.
10. Update documentation before finishing.

## Documentation

Synchronize: - driver.md - protocol-notes.md (when protocol knowledge is
verified) - command-reference.md (when extracting or correcting vendor
commands)

Never overwrite or remove user observations. If implementation validates
or contradicts an observation, update observations.md while preserving
history.

## Completion Checklist

-   Code formatted and linted.
-   Tests added or updated.
-   Existing tests pass.
-   Documentation synchronized.
-   Commands used for validation reported.
-   Remaining limitations documented.
