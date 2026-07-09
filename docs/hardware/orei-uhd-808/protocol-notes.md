# OREI UHD-808 Protocol Notes

## Purpose

This document is the engineering reference for communicating with the OREI UHD-808.

It summarizes the vendor protocol in a format convenient for driver development. It should remain synchronized with the driver implementation.

The vendor PDF remains the authoritative source.

---

# Hardware Interfaces

## RS-232

Status:
- Planned

Connector:
- TBD

Serial Settings:
- TBD

---

## Telnet

Status:
- Planned

Default Port:
- TBD

Authentication:
- TBD

Notes:
- Community reports indicate the Telnet interface is protocol-compatible with RS-232.
- Verify during implementation.

---

# Command Categories

- Routing
- Input Status
- Output Status
- EDID Management
- Scaling
- Fast Switching
- CEC
- System Configuration

---

# Command Reference

(To be populated during implementation.)

---

# Response Formats

(To be populated.)

---

# Error Responses

(To be populated.)

---

# Driver Mapping

| Driver Method | Protocol Command | Status |
|---------------|------------------|--------|
| Route Video | TBD | Planned |
| Query Routes | TBD | Planned |
| Clone EDID | TBD | Planned |
| Apply EDID | TBD | Planned |
| Configure Scaler | TBD | Planned |
| Configure Fast Switching | TBD | Planned |

---

# Unsupported Features

Document verified hardware limitations here.

---

# Firmware Notes

Document firmware-specific behavior here.

---

# Verification Status

| Feature | Status |
|----------|--------|
| Routing | Planned |
| EDID | Planned |
| Scaler | Planned |
| CEC | Planned |
| Fast Switching | Planned |
