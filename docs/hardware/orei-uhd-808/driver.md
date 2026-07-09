# OREI UHD-808 Driver

## Purpose

Provides Workspace Fabric support for the OREI UHD-808 HDMI Matrix.

This document describes the driver's capabilities, configuration, limitations, and implementation status.

---

# Driver Status

Current Phase:
- Development

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
- Telnet

Future Transport:
- RS-232

---

# Supported Operations

| Operation | Status |
|-----------|--------|
| Connect | Planned |
| Disconnect | Planned |
| Route Video | Planned |
| Query Route | Planned |
| Clone EDID | Planned |
| Apply EDID | Planned |
| Configure Scaler | Planned |
| Configure Fast Switching | Planned |
| CEC Control | Planned |

---

# Capability Report

```yaml
capabilities:
  video_routing: unknown
  route_query: unknown
  edid_clone: unknown
  edid_profile_apply: unknown
  scaler: unknown
  upscale: unknown
  fast_switching: unknown
  hpd_control: unsupported
  cec: unknown
  audio_routing: unknown
```

---

# Configuration

Example configuration:

```yaml
driver:
  type: orei-uhd-808
  host: 192.168.1.100
  port: 23
```

---

# Driver Architecture

Describe how the driver maps Workspace Fabric operations to the hardware protocol.

---

# Known Limitations

- HPD cannot currently be controlled by hardware.
- Windows display management requires the Windows Display Agent.

---

# Testing Status

| Test | Status |
|------|--------|
| Unit Tests | Planned |
| Mock Driver | Planned |
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
