# OREI UHD-808 Observations

## Purpose

This document is the field-observation and lab-notes companion for the OREI UHD-808 HDMI matrix.

Use this file to capture verified behavior, quirks, deployment notes, and lessons learned while testing or using the device with Workspace Fabric.

Codex may read this file when implementing the driver, but changes to driver behavior should be reflected in `protocol-notes.md` when they become part of the stable driver contract.

---

# Role in Reference Deployment

The UHD-808 is the reference HDMI video matrix used by Workspace Fabric.

Current reference deployment includes:

- Personal desktop
- Work laptop
- PiKVM
- Primary 4K display
- Secondary 2K display

The UHD-808 provides dynamic video routing between these resources under control of the Workspace Fabric controller.

---

# Observed Behavior: Active HDMI Link

The UHD-808 maintains an active HDMI link to upstream source devices even when a source is not currently routed to a visible display.

Impact:

- Source systems continue to believe displays remain connected.
- Windows does not automatically reconfigure the desktop when routing changes.
- Switching is effectively instantaneous because HDMI links remain trained.

This behavior is not inherently incorrect. It favors rapid switching over dynamic display enumeration.

Driver implications:

- HPD/source-disable should be reported as unsupported unless a verified hardware command is discovered.
- Windows display management should remain the responsibility of the Windows Display Agent.
- Operating-system display state and physical HDMI routing are intentionally separate concerns.

---

# EDID Management Observations

The UHD-808 supports EDID cloning from connected displays.

Observed behavior:

- EDID cloning is supported.
- EDID assignments do not automatically follow routing changes.
- EDID management should remain an explicit capability rather than an implicit part of routing.

Driver implications:

- Expose EDID clone if supported.
- Expose EDID profile application when verified.
- Allow workspace capability policies to control EDID behavior.

---

# Scaling and Upscaling Observations

The UHD-808 includes hardware scaling.

Driver implications:

- Treat scaling as an optional capability.
- Associate scaling with video routes rather than displays.
- Honor capability policies such as `prefer` and `require`.

---

# Fast Switching Observations

The UHD-808 supports rapid route switching.

Driver implications:

- Expose fast switching as an optional capability.
- Do not assume fast switching exists on all video matrices.
- Continue modeling it through the capability system.

---

# Telnet / TCP Control Observations

Physical validation completed during Milestone 3.5.

Verified behavior:

- The Telnet interface accepts the documented ASCII command set.
- RS-232 commands are protocol-compatible with the Telnet interface.
- Commands should be terminated with CRLF after the documented `!` delimiter.
- The controller echoes every command before returning its response.
- A Telnet session may begin with Telnet negotiation bytes and a welcome banner.
- The firmware banner includes the current firmware version.
- Command responses follow the echoed command and banner.

Example session:

```text
r av out 0!

****************Welcome **************
            FW Version :V2.03.01
**************************************

input 1 -> output 1
input 4 -> output 2
...
```

Driver implications:

- The transport layer must continue reading after the echoed command.
- The parser must ignore Telnet negotiation bytes.
- The parser must ignore echoed commands.
- The parser must ignore banner text.
- Route parsing should operate only on valid response lines.

This behavior belongs entirely within the driver transport layer and should remain invisible to the Workspace Fabric core.

---

# Route Query Observations

The documented route query command:

```text
r av out 0!
```

was successfully validated on physical hardware.

Observed response format:

```text
input <source> -> output <destination>
```

One line is returned for every output.

Driver implications:

- Route reconciliation can rely on hardware state rather than assumed state.
- Observed state should continue to report physical port mappings.
- The orchestration layer remains responsible for mapping physical ports back to logical resources.

---

# Relationship to Windows Display Agent

Because the UHD-808 intentionally maintains active upstream HDMI links, operating-system display management remains outside the responsibility of the video driver.

The Windows Display Agent should provide:

- Display enable/disable
- Primary display selection
- Desktop layout management
- Operating-system display state reporting

The UHD-808 driver and Windows Display Agent remain independent drivers coordinated by the transaction engine.

---

# Non-Goals for UHD-808 Driver

The UHD-808 driver should not:

- Manage Windows display settings.
- Attempt to emulate HPD behavior.
- Encode workspace policy.
- Assume all HDMI matrices expose identical capabilities.
- Translate physical ports into user-facing resource names.

---

# Lab Validation Log

## 2026-07-10 — Phase 3.5 Physical Smoke Test

Setup:

- Workspace Fabric controller connected to physical UHD-808 via Telnet.
- Physical routing configuration loaded from `physical-local.yaml`.
- Personal desktop and work laptop connected as video sources.
- Primary 4K and secondary 2K monitors connected as outputs.

Actions:

- Applied the `desktop` workspace.
- Verified route commands.
- Queried routing state.
- Performed direct Telnet protocol validation using PowerShell.

Observed Results:

- Physical routing succeeded.
- Workspace Fabric successfully controlled the UHD-808.
- Route state queries returned the expected routing table.
- Telnet command protocol matched the documented RS-232 command set.
- Telnet sessions echo commands before returning results.
- Welcome banner and firmware information are emitted during the session.
- Initial transport issues were resolved by improving response handling.
- End-to-end physical smoke tests completed successfully.

Driver Decisions:

- Continue using Telnet as the primary transport.
- Keep protocol normalization inside the driver transport.
- Preserve raw responses for diagnostics while parsing normalized responses.

Follow-up:

- Record firmware version.
- Expand physical testing to EDID management.
- Validate scaler commands.
- Validate CEC command handling.

---

# Firmware Validation

Validated firmware:

| Component | Version |
|-----------|---------|
| MCU / Web GUI | V2.03.01 |

---

# Open Questions

| Question | Status | Notes |
|----------|:------:|------|
| Does Telnet use the same command set as RS-232? | ✅ Verified | Physical testing confirms protocol compatibility. |
| Can current routing state be queried? | ✅ Verified | `r av out 0!` returns one route per output. |
| Can saved EDID profiles be applied, or only cloned? | Pending | Requires additional testing. |
| Are CEC commands exposed through the control protocol? | Pending | Documented but not yet validated. |
| Can HPD behavior be controlled by command? | Expected Unsupported | No verified command discovered. |
| Do scaler commands behave as documented? | Pending | Requires hardware validation. |
| Does EDID profile application persist across reboot? | Pending | Requires testing. |

---

# Milestone Status

Current physical validation status:

| Feature | Status |
|---------|--------|
| Telnet connectivity | ✅ Verified |
| Command protocol | ✅ Verified |
| Video routing | ✅ Verified |
| Route state query | ✅ Verified |
| Physical smoke test | ✅ Verified |
| EDID clone | Pending |
| EDID apply | Pending |
| Scaler control | Pending |
| CEC | Pending |
| ARC | Pending |
