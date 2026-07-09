# OREI UKM-404 Command Reference

## Purpose

This document is an extracted, development-friendly command reference for the
OREI UKM-404 USB 3.2 Gen 1 4x4 Matrix.

The vendor documentation remains authoritative. This file should be reviewed
against the vendor PDF before driver code depends on any command.

## Source Documents

- `UKM-404 Manual.pdf`
- Manual sections:
  - Specifications, page 6.
  - Operation Controls and Functions, pages 7-8.
  - Web GUI User Guide, pages 10-15.
  - RS-232 Commands, pages 16-20.

## Transport Summary

| Transport | Status | Details |
| --- | --- | --- |
| RS-232 | Documented | 3-pin 3.81 mm Phoenix connector. ASCII commands. Baud rate `115200` default, 8 data bits, 1 stop bit, check bit `0`. |
| TCP/IP | Documented as control interface | RJ45 100M LAN port for Web GUI and TCP/IP control. Default TCP/IP port examples show `8000`. Command framing over TCP/IP is TBD. |
| Telnet | Documented as configurable port | Network status examples show Telnet port `23`. Command framing and authentication over Telnet are TBD. |
| Web GUI | Documented | Browser UI at the device IP address. Default login shown as username `Admin`, password `1234`. |

## Protocol Framing

Line ending:

- TBD. The manual says to send ASCII commands, but does not document CR, LF, or
  CRLF requirements.

Command terminator:

- TBD. Unlike the OREI UHD-808 manual, the UKM-404 command table does not show
  a `!` terminator on command examples.

Response terminator:

- TBD.

Timeout guidance:

- TBD. The manual does not document timeout behavior.

Authentication:

- Web GUI authentication is documented.
- RS-232 authentication is not documented.
- TCP/IP and Telnet command authentication are TBD.

## Parameter Conventions

| Parameter | Meaning |
| --- | --- |
| `x=0~1` | Binary setting for some system commands, commonly off/on |
| `x=1~4` | USB device number for USB matrix commands |
| `y=1~4` | USB host number for USB matrix commands |
| `z=0~1` | Binary setting as written in some manual descriptions |
| `z=1~8` | Preset number as written in some manual descriptions |
| `xxx.xxx.xxx.xxx` | IPv4 address style value |

Notes:

- The manual sometimes names a command parameter `x` while the description
  refers to `z`. The command syntax below preserves the command code column.
- The manual's network setting feedback refers to `s net reboot!`, while the
  command table documents `set net reboot`. Treat this as ambiguous until
  verified on hardware.

## System Commands

| Command | Purpose | Parameters | Example | Response | Notes |
| --- | --- | --- | --- | --- | --- |
| `?` | List all commands | None | `?` | Command list | Manual page 16. |
| `help` | List all commands | None | `help` | Command list | Manual page 16. |
| `status` | Get device current status | None | `status` | Unit status including power, beep, USB crosspoint, and network status | Manual page 16. |
| `get model` | Get device model | None | `get model` | Example: `4x4 USB3.2 Gen1 Matrix` | Manual page 16. |
| `get version` | Get firmware version | None | `get version` | Example lines include `mcu fw version :1.00.00` and `web gui version :1.00.00` | Manual page 16. |
| `set power x` | Power the device on or off | Manual description says `z=0~1` | `set power x` | Power on response may include initialization and version lines | Example in manual uses the placeholder instead of a concrete value. Default column shows `power 1`. |
| `get power` | Get current power state | None | `get power` | `power on` or `power off` | Manual page 17. |
| `set beep x` | Enable or disable buzzer | Manual description says `z=0~1`, `0` beep off, `1` beep on | `set beep 0` | `beep on` or `beep off` | The extracted table appears internally inconsistent for example/default feedback. Verify on hardware. |
| `get beep` | Get buzzer state | None | `get beep` | `beep on` or `beep off` | Manual page 17. |
| `set lock x` | Lock or unlock front panel buttons | Manual description says `z=0~1`, `0` lock off, `1` lock on | `set lock 0` | `panel button lock on` or `panel button lock off` | The extracted table appears internally inconsistent for example/default feedback. Verify on hardware. |
| `get lock` | Get front panel button lock state | None | `get lock` | `panel button lock on/off` | Manual page 17. |
| `set baud rate x` | Set RS-232 baud rate | `x=1~6`: `1` 115200, `2` 57600, `3` 38400, `4` 19200, `5` 9600, `6` 4800 | `set baud rate 1` | `baudrate:115200` | Default is `115200`. |
| `get baud rate` | Get RS-232 baud rate | None | `get baud rate` | `baudrate:115200` | Manual page 17. |
| `reboot` | Reboot the device | None | `reboot` | `reboot...`, initialization lines, firmware version lines, `initialization finished!` | Disruptive command. |
| `reset` | Reset to factory defaults | None | `reset` | `reset to factory defaults`, initialization lines, firmware version lines, `initialization finished!` | Destructive configuration command. |

## USB Matrix Commands

| Command | Purpose | Parameters | Example | Response | Notes |
| --- | --- | --- | --- | --- | --- |
| `set device x in host y` | Route USB device `x` to host `y` | `x=1~4`, `y=1~4` | `set device 1 in host 1` | Example: `set device 1 in host 1`; default/state lines may use `device 1->host 1` | Manual page 17. |
| `get device x in host` | Get selected host for USB device `x` | `x=1~4` | `get device 1 in host` | Example: `device 1 in host 3` | Manual page 18. |

Default route state:

- The manual default column appears to list:
  - `device 1->host 1`
  - `device 2->host 1`
  - `device 3->host 1`
  - `device 4->host 1`
- Verify the actual power-on/default state on hardware.

## Preset Commands

| Command | Purpose | Parameters | Example | Response | Notes |
| --- | --- | --- | --- | --- | --- |
| `set save preset x` | Save matrix state for all devices and hosts to preset | Description says `z=1~8` | `set save preset 1` | Save response plus route lines | The extracted table shows `save to preset 2:` for example `set save preset 1`; verify exact response. |
| `set recall preset x` | Recall saved preset scenario | Description says `z=1~8` | `set recall preset 1` | `recall from preset 1:` plus route lines | Manual page 18. |
| `set clear preset x` | Clear stored preset scenario | Description says `z=1~8` | `set clear preset 1` | `clear preset 1` | Manual page 18. |
| `get preset x` | Get preset information | Description says `z=1~8` | `get preset 1` | `preset 1:` followed by `device N->host M` route lines | Manual page 18. |

Example preset response:

```text
preset 1:
device 1->host 1
device 2->host 2
device 3->host 3
device 4->host 4
```

## Network Commands

| Command | Purpose | Parameters | Example | Response | Notes |
| --- | --- | --- | --- | --- | --- |
| `get ipconfig` | Get current IP configuration | None | `get ipconfig` | IP mode, IP, subnet mask, gateway, TCP/IP port, Telnet port, MAC address | Manual pages 10 and 18. |
| `get mac addr` | Get network MAC address | None | `get mac addr` | Example: `mac address: 00:1c:91:03:80:01` | Manual page 18. |
| `set ip mode z` | Set network IP mode | `z=0~1`, `0` static, `1` DHCP | `set ip mode 0` | `set ip mode:static.` plus reboot/repower instruction | Default column shows `ip mode:dhcp`; page 10 example shows static IP mode. Verify default on hardware. |
| `get ip mode` | Get network IP mode | None | `get ip mode` | Example: `ip mode: static` | Manual page 18. |
| `set ip addr xxx.xxx.xxx.xxx` | Set network IP address | IPv4 address | `set ip addr 192.168.0.100` | `set ip dress: 192.168.0.100` plus reboot/repower instruction | Manual typo appears to say `dress`. DHCP mode may reject static address changes. |
| `get ip addr` | Get network IP address | None | `get ip addr` | Example: `ip address: 192.168.0.100` | Manual page 19. |
| `set subnet xxx.xxx.xxx.xxx` | Set network subnet mask | IPv4 subnet mask | `set subnet xxx.xxx.xxx.xxx` | `set subnet mask: 255.255.255.0` plus reboot/repower instruction | DHCP mode may reject static subnet changes. |
| `get subnet` | Get network subnet mask | None | `get subnet` | Example: `subnet mask: 255.255.255.0` | Manual page 19. |
| `set gateway xxx.xxx.xxx.xxx` | Set network gateway | IPv4 address | `set gateway 192.168.0.1` | `set gateway: 192.168.0.1` plus reboot/repower instruction | DHCP mode may reject static gateway changes. |
| `get gateway` | Get network gateway | None | `get gateway` | Example: `gateway:192.168.0.1` | Manual page 19. |
| `set tcp/ip port x` | Set network TCP/IP port | `x=1~65535` | `set tcp/ip port 8000` | `set tcp/ip port:8000` | Manual page 19. |
| `get tcp/ip port` | Get network TCP/IP port | None | `get tcp/ip port` | `tcp/ip port:8000` | Manual page 19. |
| `set telnet port x` | Set network Telnet port | `x=1~65535` | `set telnet port 23` | `set telnet port:23` | Manual page 19. |
| `get telnet port` | Get network Telnet port | None | `get telnet port` | `telnet port:23` | Manual page 20. |
| `set net reboot` | Reboot network modules | None | `set net reboot` | Network reboot text followed by IP configuration | Manual page 20. |

Example `get ipconfig` response:

```text
ip mode: static
ip: 192.168.0.100
subnet mask: 255.255.255.0
gateway: 192.168.0.1
tcp/ip port=8000
telnet port=23
mac address: 00:1c:91:03:80:01
```

Network setting notes:

- The manual says static network changes require network reboot or device
  repower before they apply.
- The manual feedback for static network setters can include
  `dhcp on, device can't config ... set dhcp off first.`
- The manual references `s net reboot!` in several network setter responses,
  but the command table documents `set net reboot`.

## Web GUI Controls

The Web GUI is not a command API, but it exposes control and configuration
surfaces that matter for driver validation.

| Web GUI page | Documented behavior |
| --- | --- |
| Login | Username `Admin`, default password `1234`, selectable language. |
| Information | Model, installed firmware version, and network settings. |
| Matrix | Select host for device 1-4. Save, recall, and clear up to 8 presets. |
| USB | Rename each host or device. |
| Network | Modify IP mode, IP address, gateway, subnet mask, Telnet port, and domain name. |
| System | Change account password, panel lock, beep, serial baud rate, reboot, restore factory settings, and firmware update. |

## Unsafe or Caution Commands

| Command | Risk | Notes |
| --- | --- | --- |
| `set device x in host y` | Interrupts active USB device routing | May disconnect devices from a host. |
| `set save preset x` | Changes persistent preset state | Saves current matrix state. |
| `set recall preset x` | Changes active USB routes | Applies a saved route scenario. |
| `set clear preset x` | Deletes persistent preset state | Clears a stored scenario. |
| `set power x` | Interrupts device operation | Power semantics require hardware verification. |
| `set beep x` | Changes device setting | Persistent behavior TBD. |
| `set lock x` | Changes front panel accessibility | Persistent behavior TBD. |
| `set baud rate x` | Changes serial transport settings | Can break the active control session if the caller does not reconnect at the new baud rate. |
| `reboot` | Interrupts device operation | Device reboot. |
| `reset` | Factory reset | Destructive configuration command. |
| Network setters | Changes management-plane connectivity | Includes `set ip mode z`, `set ip addr ...`, `set subnet ...`, `set gateway ...`, `set tcp/ip port x`, and `set telnet port x`. |
| `set net reboot` | Interrupts management-plane connectivity | Reboots network modules. |
| Web GUI firmware update | Changes firmware | Manual documents upload-based update, not a command. |

## Response Formats

The manual examples are human-readable ASCII responses rather than a formal
grammar.

Known response patterns:

```text
device 1->host 1
device 1 in host 3
ip mode: static
tcp/ip port=8000
telnet port:23
mcu fw version :1.00.00
web gui version :1.00.00
```

Some commands, especially `reboot`, `reset`, and `set net reboot`, produce
multiple response lines.

## Error Responses

Documented network-setting rejection examples:

```text
dhcp on, device can't config static address, set dhcp off first.
dhcp on, device can't config subnet mask, set dhcp off first.
dhcp on, device can't config gateway, set dhcp off first.
```

TBD:

- Invalid command response.
- Invalid parameter response.
- Invalid USB device or host port response.
- Busy or unavailable device response.
- Transport timeout behavior.
- Malformed response behavior.

## Open Questions

- What line ending is required or accepted after commands?
- Are the RS-232 command strings accepted unchanged over TCP/IP port `8000`?
- Are the RS-232 command strings accepted unchanged over Telnet port `23`?
- Do TCP/IP or Telnet command sessions require authentication?
- Does `set power x` use `x=0~1`, and which value means on versus standby?
- Are `set beep x` and `set lock x` example responses correct in the manual?
- Is the default route state all devices to host 1, as the command table
  appears to show?
- Is route query always supported through `get device x in host`?
- What are the exact responses for invalid ports and unsupported commands?
- Does the device retain routes, presets, baud rate, and network settings
  across power loss?
