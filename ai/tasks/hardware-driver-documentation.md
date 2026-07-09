# Hardware Driver Documentation Task

## Purpose

Maintain consistent documentation for every Workspace Fabric hardware
driver.

## Driver Documentation Set

Each device directory should contain:

-   Vendor manual(s)
-   command-reference.md
-   protocol-notes.md
-   observations.md
-   driver.md

## Responsibilities

### command-reference.md

AI-maintained extraction of vendor commands.

Update when: - New commands are implemented. - Vendor documentation is
clarified.

Do not invent commands.

### protocol-notes.md

Engineering interpretation of the protocol.

Record: - Transport details - Driver mappings - Response formats -
Verified protocol behavior - Unsupported features

### observations.md

Primarily human-maintained lab notebook.

Record: - Firmware quirks - Hardware limitations - Unexpected behavior -
Deployment notes

Append discoveries rather than rewriting history.

### driver.md

AI-maintained driver contract.

Keep synchronized with implementation:

-   Supported operations
-   Capability report
-   Tested firmware
-   Configuration
-   Known limitations
-   Testing status
-   Change log

## Documentation Rules

-   Vendor manual is the authoritative protocol source.
-   command-reference.md mirrors vendor information.
-   protocol-notes.md explains implementation.
-   observations.md captures reality.
-   driver.md documents Workspace Fabric behavior.

If documents and implementation disagree, stop and resolve the conflict
instead of silently updating only one source.
