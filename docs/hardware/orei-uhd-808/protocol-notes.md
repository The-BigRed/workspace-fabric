# OREI UHD-808 Protocol Notes

## Purpose

This document is the driver-facing protocol interpretation for communicating
with the OREI UHD-808.

The vendor PDF remains the authoritative source. The transcribed command list
for driver implementation lives in
[`command-reference.md`](command-reference.md).

## Hardware Interfaces

### RS-232

Status:

- Planned

Connector:

- D-Sub 9 control port.

Serial settings:

| Setting | Value |
| --- | --- |
| Baud rate | `115200` default |
| Data bits | `8` |
| Stop bits | `1` |
| Check bit | `0` |

Notes:

- Commands are ASCII text terminated by the `!` delimiter.
- The manual does not specify whether CR, LF, or CRLF is accepted after `!`.
- The manual does not specify command timeout behavior.

### TCP/IP and Telnet

Status:

- Planned

Connector:

- RJ45 TCP/IP control port.

Ports:

- TCP/IP port is configurable with the documented network commands.
- Telnet port is configurable with the documented network commands.
- The manual examples show inconsistent Telnet port values; verify the default
  on hardware before treating any value as canonical.

Authentication:

- TBD. The manual documents Web GUI login, but does not document authentication
  for RS-232, TCP/IP, or Telnet command sessions.

Notes:

- Community reports indicate the Telnet interface is protocol-compatible with
  RS-232. Verify during implementation.
- The manual exposes both TCP/IP and Telnet port settings. Driver transport
  selection should remain explicit and configurable until hardware testing
  confirms behavior.

## Command Reference

Use [`command-reference.md`](command-reference.md) for command syntax,
parameters, response examples, and caution notes. Do not duplicate the full
command table here.

Command areas covered by the vendor manual:

- Power and reboot.
- System information and settings.
- Video routing.
- HDMI output stream and scaler settings.
- EDID assignment and EDID data query.
- ARC.
- CEC.
- Network configuration.

## Response Formats

Responses are documented as human-readable ASCII text. The manual examples are
not a formal grammar, so the first driver should parse narrowly for the
commands it issues and preserve raw responses for diagnostics.

Known response styles:

- Route query responses use lines like `input 1 -> output 1`.
- Link query responses use lines like `hdmi input 1: connect`.
- EDID data responses begin with `EDID:` followed by hexadecimal bytes.
- Network query responses are labeled text fields.
- Reboot and reset commands may emit multiple startup/status lines.

## Error Responses

TBD. The manual does not document error response formats. Hardware testing
should capture responses for malformed commands, unsupported parameters, busy
state, disconnected sessions, and invalid route requests.

## Driver Mapping

| Driver Method | Protocol Command | Status |
| --- | --- | --- |
| Route video | `s in x av out y!` | Planned |
| Query routes | `r av out y!` | Planned |
| Query input link | `r link in x!` | Planned |
| Query output link | `r link out y!` | Planned |
| Apply EDID | `s edid in x from z!` | Planned |
| Query EDID assignment | `r edid in x!` | Planned |
| Query output EDID data | `r edid data hdmi y!` | Planned |
| Configure scaler | `s hdmi y scaler z!` | Planned |
| Query scaler | `r hdmi y scaler!` | Planned |
| Configure output stream | `s hdmi y stream z!` | Planned |
| Query output stream | `r hdmi y stream!` | Planned |
| Configure ARC | `s hdmi y arc z!` | Planned |
| Query ARC | `r hdmi y arc!` | Planned |
| Send CEC | `s cec ...!` command family | Planned |
| Query full status | `r status!` | Planned |

## Unsupported or Unverified Features

- No explicit fast-switching command was found in the vendor manual. Treat fast
  switching as unsupported until hardware testing proves otherwise.
- Route state query support exists in the manual, but output format should be
  validated on hardware before relying on it for reconciliation.
- EDID clone slots `24~31` are documented as copies from HDMI outputs `1~8`;
  behavior should be verified before exposing automated clone workflows.

## Firmware Notes

Firmware-specific behavior is unknown. The manual documents `r fw version!`
returning MCU boot, MCU app, and Web GUI versions. Record observed firmware
versions during driver validation.

## Verification Status

| Feature | Status |
| --- | --- |
| RS-232 transport | Planned |
| TCP/IP transport | Planned |
| Telnet transport | Planned |
| Routing | Planned |
| Route query | Planned |
| EDID assignment | Planned |
| EDID data query | Planned |
| Scaler | Planned |
| ARC | Planned |
| CEC | Planned |
| Network configuration | Planned |
