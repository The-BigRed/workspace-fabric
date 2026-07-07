# Reference Platform

## Purpose
Defines the reference hardware used to validate Workspace Fabric.

## Hardware Philosophy
Reference hardware validates the architecture but does not define it.

## Current Reference Platform
- Personal desktop
- Work laptop
- OREI UHD-808
- Two OREI UKM404 USB matrices
- Primary 4K monitor
- Secondary 2K monitor
- PiKVM v4 Mini
- Future Windows Display Agent

## Reference Hardware Details

### Desktop Host

The desktop position is a custom home-built desktop computer.

Known details:

- Custom-built desktop PC.
- NVIDIA GPU.
- Dual DisplayPort outputs.
- DisplayPort-to-HDMI cables connected to the OREI UHD-808.
- Two USB upstream connections, one to each OREI UKM-404 USB matrix.
- CPU:  i9-12900K
- Motherboard:  Z790 GAMING WIFI7
- RAM:  32GB DDR5
- GPU:  NVidia GeForce RTX 2080Ti
- Operating System:  Windows 11 2025H2

### Laptop Host

The laptop position is normally occupied by the author's work laptop.

Known details:

- Dell Pro 16 Plus laptop.
- Dell WD19TB4 Dock.
- Dual DisplayPort outputs from the dock.
- DisplayPort-to-HDMI cables connected to the OREI UHD-808.
- Two USB upstream connections, one to each OREI UKM-404 USB matrix.

### Displays

Primary display:

- ViewSonic VX4380.
- Primary 4K monitor.

Secondary display:

- MSI MP275Q.
- Secondary 2K monitor.

### Matrix Hardware

Video matrix:

- OREI UHD-808.
- IP address: `172.24.3.192/23`.

USB matrix A:

- OREI UKM-404.
- IP address: `172.24.3.193/23`.

USB matrix B:

- OREI UKM-404.
- IP address: `172.24.3.194/23`.

### Firmware Versions

Firmware versions refer to the embedded firmware/software running on the matrix devices and any other managed hardware.

For this reference platform, firmware versions should eventually be recorded for:

- OREI UHD-808:  V2.03.01/V2.03
- OREI UKM-404 A:  V1.00.05/V2.00.05
- OREI UKM-404 B:  V1.00.05/V2.00.05
- PiKVM v4 Mini:

### Network Details

All Workspace Fabric reference devices currently exist on the same local subnet.

Known network assignments:

| Device | Address |
|---|---|
| OREI UHD-808 | `172.24.3.192/23` |
| OREI UKM-404 A | `172.24.3.193/23` |
| OREI UKM-404 B | `172.24.3.194/23` |

### Controller VM

The Workspace Fabric controller VM has not been built yet.

Planned controller:

- Debian 12 base installation.
- Hosted as a VM.
- Located on the same local subnet as the matrix devices.
- Initial deployment target for the Workspace Fabric control plane.

TODO (Author): Add VM host platform, vCPU, RAM, disk size, hostname, IP address, and deployment method once built.

## Driver Support Tiers
Tier 1: Reference hardware
Tier 2: Community supported
Tier 3: Experimental

## Future Expansion
Additional matrices, enterprise IP-KVM, BMC consoles, software agents, and broadcast hardware.
