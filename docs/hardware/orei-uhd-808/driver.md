# OREI UHD-808 Driver

## Purpose

Provides Workspace Fabric support for the OREI UHD-808 HDMI Matrix.

This document describes the driver's capabilities, configuration, limitations, and implementation status.

---

# Driver Status

Current Phase:
- Development

Current Milestone:
- Phase 3.2 OREI UHD-808 Video Driver

Driver Version:
- Unreleased

---

# Supported Hardware

| Model | Status |
|--------|--------|
| OREI UHD-808 | Supported |

Firmware Tested:
- TBD

---

# Transport

Current Transport:
- TCP/Telnet-style socket command transport implemented.

Future Transport:
- RS-232

Verification:
- Mocked transport tests cover command formatting, route application, route query parsing, and
  transport failures.
- Physical TCP/Telnet and RS-232 validation is still pending.

---

# Supported Operations

| Operation | Status |
|-----------|--------|
| Connect | Implemented, physical validation pending |
| Disconnect | Implemented, physical validation pending |
| Route Video | Implemented with mocked transport |
| Query Route | Implemented with mocked transport |
| Clone EDID | Planned |
| Apply EDID | Planned |
| Configure Scaler | Planned |
| Configure Fast Switching | Unsupported until a hardware command is verified |
| CEC Control | Planned |

---

# Capability Report

```yaml
capabilities:
  video_routing: supported
  route_query: supported
  edid_clone: unknown
  edid_profile_apply: unknown
  scaler: unknown
  upscale: unknown
  fast_switching: unsupported
  hpd_control: unsupported
  cec: unknown
  audio_routing: unknown
```

---

# Configuration

Example configuration:

```yaml
driver:
  type: orei_uhd808
  fabric: local_workspace
  connection:
    transport: telnet
    host: 192.168.1.100
    port: 23
    timeout_seconds: 2
video_sources:
  desktop_dp1:
    driver: uhd808
    port: 1
  desktop_dp2:
    driver: uhd808
    port: 2
video_outputs:
  video_out1:
    driver: uhd808
    port: 1
  video_out2:
    driver: uhd808
    port: 2
```

Configuration notes:

- Video source and output resources carry the physical port attachments.
- The orchestration layer resolves user-facing source/display IDs to `input_port` and
  `output_port` before invoking the driver.
- The UHD-808 driver does not depend on environment-specific resource names.

---

# Driver Architecture

The driver maps Workspace Fabric `video_route` actions containing `input_port` and `output_port`
to UHD-808 route commands:

```text
s in x av out y!
```

It queries route state with:

```text
r av out 0!
```

Route responses are parsed from lines shaped like:

```text
input 1 -> output 2
```

The driver reports device-local port routes in observed state. The orchestration layer may correlate
those ports back to user-facing resources when it has the relevant resource graph context.

---

# Known Limitations

- HPD cannot currently be controlled by hardware.
- Fast switching is not exposed until a verified protocol command exists.
- TCP/Telnet command framing and physical connection behavior still require hardware validation.
- Windows display management requires the Windows Display Agent.

---

# Testing Status

| Test | Status |
|------|--------|
| Unit Tests | Implemented for mocked transport |
| Mock Driver | Existing Phase 2 mock remains separate |
| Physical Routing | Planned |
| EDID | Planned |
| CEC | Planned |

---

# Future Enhancements

Document planned improvements and optional capabilities.

---

# Change Log

## YYYY-MM-DD

- Initial driver scaffold.

## 2026-07-09

- Implemented Milestone 3.2 driver routing/query behavior with mocked transport tests.
