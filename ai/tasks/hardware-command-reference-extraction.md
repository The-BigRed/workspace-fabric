# Hardware Command Reference Extraction Task

## Purpose

Use this task when adding a new hardware device to Workspace Fabric and the vendor documentation contains a console, serial, Telnet, TCP, HTTP, REST, or other command/API reference.

The goal is to extract the vendor command reference into a development-friendly Markdown document before implementing the driver.

This task should produce or update:

- `command-reference.md`
- `protocol-notes.md`

It should not implement driver code unless explicitly requested in a separate task.

---

## Expected Device Documentation Layout

Each hardware device should have its own directory under `docs/hardware/`.

Example:

```text
/docs/hardware/<vendor-model>/
├── <vendor-manual>.pdf
├── command-reference.md
├── protocol-notes.md
├── observations.md
└── driver.md
```

Document roles:

- Vendor manual: authoritative vendor source, read-only.
- `command-reference.md`: extracted vendor command/API reference.
- `protocol-notes.md`: engineering interpretation, protocol behavior, driver mappings, quirks, and open questions.
- `observations.md`: human and lab-discovered hardware behavior.
- `driver.md`: Workspace Fabric driver documentation and implementation status.

---

## Codex Task Prompt

```text
Create or update docs/hardware/<device-directory>/command-reference.md from the vendor documentation for <device-name>.

Read first:
- AGENTS.md
- PROJECT_STATUS.md
- docs/driver-contract.md
- docs/hardware/<device-directory>/<vendor-manual>.pdf
- docs/hardware/<device-directory>/protocol-notes.md
- docs/hardware/<device-directory>/observations.md
- docs/hardware/<device-directory>/driver.md

Task:
Extract the vendor command/API reference into docs/hardware/<device-directory>/command-reference.md.

Requirements:
- Preserve command syntax exactly where possible.
- Group commands by category.
- Include command purpose, parameters, valid values, examples, expected responses, and notes.
- Include transport details such as serial settings, Telnet port, TCP port, authentication, framing, delimiters, line endings, and timeout expectations when documented.
- Include page or section references back to the vendor manual where practical.
- Mark unclear, missing, or ambiguous details as TBD.
- Mark commands that appear unsafe, destructive, factory-reset-related, or configuration-changing as caution items.
- Do not invent commands, responses, or behavior.
- Do not implement driver code in this task.
- Do not change core architecture documents in this task.
- Update protocol-notes.md only to reference command-reference.md and record any protocol-level interpretation needed for future driver work.
- If the vendor documentation is incomplete or ambiguous, record open questions instead of guessing.

Acceptance criteria:
- command-reference.md exists and is organized by command category.
- command syntax is copied or faithfully transcribed from the vendor documentation.
- response formats and examples are captured where available.
- ambiguous details are explicitly marked TBD.
- protocol-notes.md references command-reference.md instead of duplicating the full command list.
- No driver code is changed.
```

---

## Suggested `command-reference.md` Format

```markdown
# <Device Name> Command Reference

## Purpose

This document is an extracted, development-friendly command reference for <Device Name>.

The vendor documentation remains authoritative.

---

## Source Documents

- `<vendor-manual>.pdf`
- Manual section/pages: TBD

---

## Transport Summary

| Transport | Status | Details |
|---|---|---|
| RS-232 | TBD | TBD |
| Telnet | TBD | TBD |
| TCP | TBD | TBD |
| HTTP/REST | TBD | TBD |

---

## Protocol Framing

Line Ending:
- TBD

Command Terminator:
- TBD

Response Terminator:
- TBD

Timeout Guidance:
- TBD

Authentication:
- TBD

---

## Command Categories

- Routing
- Status / Query
- EDID
- Scaling
- Audio
- CEC
- USB
- System
- Network
- Presets / Scenes
- Other

Remove categories that do not apply.

---

## Routing Commands

| Command | Purpose | Parameters | Example | Response | Notes |
|---|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD | TBD |

---

## Status / Query Commands

| Command | Purpose | Parameters | Example | Response | Notes |
|---|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD | TBD |

---

## Configuration Commands

| Command | Purpose | Parameters | Example | Response | Notes |
|---|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD | TBD |

---

## Unsafe or Caution Commands

Commands in this section may change persistent configuration, reset the device, interrupt active routes, or have unclear side effects.

| Command | Risk | Notes |
|---|---|---|
| TBD | TBD | TBD |

---

## Response Formats

Document common response patterns here.

```text
TBD
```

---

## Error Responses

Document known error responses here.

```text
TBD
```

---

## Open Questions

- TBD
```

---

## Suggested `protocol-notes.md` Update

After creating `command-reference.md`, ensure `protocol-notes.md` includes a section like this:

```markdown
# Command Reference

The extracted vendor command table lives in:

- `command-reference.md`

This document does not duplicate the full command list. It records protocol behavior, driver mappings, verified quirks, implementation notes, and open questions discovered during driver development.
```

---

## Recommended Workflow

1. Add the vendor manual to the device directory.
2. Run this extraction task.
3. Review `command-reference.md` manually for transcription errors.
4. Commit the extracted reference.
5. Start the driver scaffold task.
6. As driver behavior is verified, update:
   - `protocol-notes.md` for protocol interpretation and driver mappings.
   - `observations.md` for real-world hardware behavior.
   - `driver.md` for implemented driver capability and status.

---

## Notes for AI Agents

- Prefer explicit uncertainty over invented behavior.
- Keep vendor facts separate from Workspace Fabric design decisions.
- Do not treat a single device's limitations as generic architecture unless an ADR or core document says so.
- Keep command extraction separate from implementation so command transcription can be reviewed before code depends on it.
