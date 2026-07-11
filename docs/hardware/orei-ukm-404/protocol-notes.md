# OREI UKM-404 Protocol Notes

## Purpose

This document is the driver-facing protocol interpretation for communicating
with the OREI UKM-404 USB matrix.

The vendor manual remains authoritative. The extracted vendor command table
for driver implementation lives in
[`command-reference.md`](command-reference.md).

## Source Material

- Vendor manual: `UKM-404 Manual.pdf`.
- Command extraction: [`command-reference.md`](command-reference.md).
- Real-world observations: [`observations.md`](observations.md).
- Workspace Fabric driver status: [`driver.md`](driver.md).

## Hardware Interfaces

### RS-232

Status:

- Documented by vendor manual.
- Implemented in driver through configurable serial transport.
- Physical validation pending.

Connector:

- 3-pin 3.81 mm Phoenix connector.

Serial settings:

| Setting | Value |
| --- | --- |
| Baud rate | `115200` default |
| Data bits | `8` |
| Stop bits | `1` |
| Check bit | `0` |

Notes:

- Commands are ASCII text.
- The manual does not document command line endings.
- The manual does not show a `!` command terminator for UKM-404 commands.
- The command table uses plain commands such as `status`, `get ip addr`, and
  `set device x in host y`.

### TCP/IP and Telnet

Status:

- Documented as management/control interfaces.
- Implemented in driver through configurable TCP/Telnet-style socket transport.
- Command framing requires physical verification.

Connector:

- RJ45 100M LAN port.

Documented defaults and examples:

| Item | Value |
| --- | --- |
| Default IP address | `192.168.0.100` |
| TCP/IP port | `8000` |
| Telnet port | `23` |
| Web GUI username | `Admin` |
| Web GUI default password | `1234` |

Notes:

- The manual says the LAN port supports Web GUI and TCP/IP control.
- The manual exposes both TCP/IP and Telnet ports in network status/settings.
- The RS-232 command table is the only explicit command table. Whether those
  commands are accepted unchanged over TCP/IP or Telnet is TBD.
- TCP/IP and Telnet authentication requirements are TBD.

## Command Reference

Use [`command-reference.md`](command-reference.md) for command syntax,
parameters, response examples, caution items, and open questions. Do not
duplicate the full command list here.

Command areas covered by the vendor manual:

- System status and settings.
- USB device-to-host routing.
- Route query.
- Presets.
- Network configuration.
- Web GUI controls.

## Response Formats

Responses are documented as human-readable ASCII text rather than a formal
grammar. The first driver should parse only the responses required for its
supported actions and preserve raw responses for diagnostics.

Known response styles:

- Route state lines use forms like `device 1->host 1`.
- Per-device route query can return forms like `device 1 in host 3`.
- Network status is returned as labeled text fields.
- Firmware status includes MCU and Web GUI version lines.
- Reboot, reset, and network reboot commands may emit multiple response lines.

## Error Responses

The manual documents DHCP-related rejection text for static network settings,
for example:

```text
dhcp on, device can't config static address, set dhcp off first.
```

TBD:

- Invalid command response.
- Invalid USB device or host port response.
- Unsupported command response.
- Busy or unavailable hardware response.
- Communication timeout behavior.
- Malformed response behavior.

## Driver Mapping

The orchestration layer must resolve Workspace Fabric USB device/host IDs to UKM-404
device-local ports before calling the driver. The driver consumes `device_port` and `host_port`
values and must not depend on deployment-specific resource names.

| Workspace Fabric Driver Method | Protocol Command | Status |
| --- | --- | --- |
| Connect | Transport-specific open | Implemented, physical validation pending |
| Disconnect | Transport-specific close | Implemented, physical validation pending |
| Health | Connection state | Implemented |
| Route USB device to host | `set device x in host y` | Implemented with mocked transport |
| Query route state | `get device x in host` | Implemented with mocked transport |
| Query full state | Per-device route queries | Implemented with mocked transport |
| Query capabilities | Static driver capability report plus verified transport support | Implemented |
| Query firmware/system info | `get model`, `get version` | Planned |
| Configure network | `set ip mode z`, `set ip addr ...`, `set subnet ...`, `set gateway ...`, `set tcp/ip port x`, `set telnet port x` | Not planned for initial driver |
| Reboot network module | `set net reboot` | Not planned for initial driver |
| Factory reset | `reset` | Not planned for initial driver |

## Capability Verification

Initial expected capability report:

```yaml
capabilities:
  usb_routing: supported
  per_device_routing: supported
  route_query: supported
  usb3: supported
  host_emulation: unknown
  device_emulation: unknown
```

Notes:

- `route_query` is documented through `get device x in host`, but should remain
  hardware-verified before the driver depends on it for reconciliation.
- USB 3.2 Gen 1 support is documented by the vendor manual.
- Host emulation and device emulation are not described by the vendor manual.

## Unsupported or Unverified Features

- Host emulation: not documented.
- Device emulation: not documented.
- Cross-matrix USB routing: not supported by a single UKM-404 driver instance.
- TCP/IP command framing: unverified.
- Telnet command framing: unverified.
- Command line endings and response terminators: undocumented.
- Exact default route state: unverified.

## Firmware Notes

Firmware-specific behavior is unknown. The manual documents `get version`
returning MCU firmware and Web GUI versions. Record observed firmware versions
during driver validation.

## Verification Status

| Feature | Status | Notes |
| --- | --- | --- |
| RS-232 transport | Implemented, physical validation pending | Vendor documented |
| TCP/IP transport | Implemented, physical validation pending | Control port documented, command framing TBD |
| Telnet transport | Implemented, physical validation pending | Port documented, command framing TBD |
| Device-to-host routing | Implemented with mocked transport | `set device x in host y` |
| Route query | Implemented with mocked transport | `get device x in host`; verify on hardware |
| Multiple instances | Planned | Required by reference deployment |
| USB 3 support | Documented | USB 3.2 Gen 1 |
| Host emulation | Unknown | Not documented |
| Device emulation | Unknown | Not documented |
