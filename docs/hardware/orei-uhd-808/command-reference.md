# OREI UHD-808 Command Reference

This reference is transcribed from `UHD-808 manual.pdf`, especially the
RS-232 Command section on manual pages 21-30. It is intended as the
driver-facing command source for future OREI UHD-808 work.

## Protocol Summary

| Item | Value |
| --- | --- |
| Command encoding | ASCII text commands |
| Command delimiter | `!` |
| Parameter placeholders | `x` and `y` are command parameters in the manual |
| RS-232 baud rate | `115200` default |
| RS-232 data bits | `8` |
| RS-232 stop bits | `1` |
| RS-232 check bit | `0` |
| TCP/IP control | RJ45 control port, configurable TCP/IP port |
| Telnet control | Configurable Telnet port |

TBD:

- The manual documents `!` as the delimiter but does not state whether CR, LF,
  or CRLF is accepted or required after it.
- The manual does not document command timeout behavior.
- The manual does not document authentication for RS-232, TCP/IP, or Telnet
  commands.
- The manual examples show both TCP/IP and Telnet ports. Which port should be
  preferred by a driver depends on empirical testing.

## Parameter Conventions

| Parameter | Meaning |
| --- | --- |
| `x=0~8` | Usually HDMI input, where `0` means all inputs |
| `y=0~8` | Usually HDMI output, where `0` means all outputs |
| `z=0~1` | Binary setting, commonly `0` off/disable and `1` on/enable |
| `xxx.xxx.xxx.xxx` | IPv4 address style value |

## Power Commands

| Command | Description | Parameters | Example | Documented response |
| --- | --- | --- | --- | --- |
| `s power z!` | Power the unit off or on | `z=0~1`, `0` off, `1` on | `s power 1!` | `Power on`; startup messages may include `System Initializing...` and `Initialization Finished!` |
| `r power!` | Read power state | None | `r power!` | `power on` or `power off` |
| `s reboot!` | Reboot the unit | None | `s reboot!` | `Reboot...`, startup messages, and firmware version output |

## System Commands

| Command | Description | Parameters | Example | Documented response |
| --- | --- | --- | --- | --- |
| `help!` | List supported commands | None | `help!` | Command list |
| `r type!` | Read device model | None | `r type!` | Example in manual: `HDP-MXB88DA` |
| `r status!` | Read full unit status | None | `r status!` | Includes power, beep, lock, link state, routes, EDID, scaler, and network status |
| `r fw version!` | Read firmware versions | None | `r fw version!` | Includes `MCU BOOT`, `MCU APP`, and `WEB GUI` versions |
| `r link in x!` | Read HDMI input connection state | `x=0~8`, `0` all | `r link in 1!` | Example: `hdmi input 1: connect` |
| `r link out y!` | Read HDMI output connection state | `y=0~8`, `0` all | `r link out 1!` | Example: `hdmi output 1: connect` |
| `s reset!` | Reset to factory defaults | None | `s reset!` | `Reset to factory defaults`, startup messages, and firmware version output |
| `s beep z!` | Enable or disable buzzer | `z=0~1` | `s beep 1!` | `beep on` or `beep off` |
| `r beep!` | Read buzzer state | None | `r beep!` | `beep on` or `beep off` |
| `s lock z!` | Lock or unlock front panel buttons | `z=0~1`, `0` lock off, `1` lock on | `s lock 1!` | `panel button lock on` or `panel button lock off` |
| `r lock!` | Read front panel lock state | None | `r lock!` | `panel button lock on` or `panel button lock off` |
| `s lcd on time z!` | Set LCD backlight remain-on mode | `z=0~4`: `0` off, `1` always on, `2` 15 seconds, `3` 30 seconds, `4` 60 seconds | `s lcd on time 1!` | Response text is ambiguous in the manual extraction; verify on hardware |
| `r lcd mode!` | Read LCD backlight mode | None | `r lcd mode!` | Example: `lcd always on` |
| `s save preset z!` | Save current switch state to preset | `z=1~8` | `s save preset 1!` | `save to preset 1` |
| `s recall preset z!` | Recall a saved preset | `z=1~8` | `s recall preset 1!` | `recall from preset 1` |
| `s clear preset z!` | Clear a saved preset | `z=1~8` | `s clear preset 1!` | `clear preset 1` |
| `r preset z!` | Read preset routing information | `z=1~8` | `r preset 1!` | Video/audio crosspoint data |
| `s logo1 ****************!` | Set LCD first-line logo text | Up to 16 characters | `s logo1 Initializing...!` | Example: `logo1:Initializing...` |
| `s logo2 ****************!` | Set LCD second-line logo text | Up to 16 characters | `s logo2 HDP-MXB-88DA!` | Example response text is inconsistently formatted in the manual |
| `s baud rate xxx!` | Set RS-232 baud rate | `xxx` is one of `115200`, `57600`, `38400`, `19200`, `9600`, `4800` | `s baud rate 115200!` | `Baudrate:115200` |
| `r baud rate!` | Read RS-232 baud rate | None | `r baud rate!` | `Baudrate:115200` |
| `s id z!` | Set control ID | `z=000~999` | `s id 888!` | Example: `id 888!` |

## Video Routing Commands

| Command | Description | Parameters | Example | Documented response |
| --- | --- | --- | --- | --- |
| `s in x av out y!` | Route HDMI input to HDMI output | `x=1~8`; `y=0~8`, `0` all outputs | `s in 1 av out 2!` | `input 1 -> output 2` |
| `r av out y!` | Read route for one or all HDMI outputs | `y=0~8`, `0` all outputs | `r av out 0!` | One line per output, such as `input 1 -> output 1` |
| `s hdmi y stream z!` | Enable or disable HDMI output stream | `y=0~8`, `0` all outputs; `z=0~1`, `0` disable, `1` enable | `s hdmi 1 stream 1!` | Output stream enabled or disabled text |
| `r hdmi y stream!` | Read HDMI output stream state | `y=0~8`, `0` all outputs | `r hdmi 1 stream!` | Example: `Enable hdmi output 1 stream` |
| `s hdmi y scaler z!` | Set HDMI output scaler mode | `y=0~8`, `0` all outputs; `z=1~3`, `1` bypass, `2` 4K to 1080p, `3` auto | `s hdmi 1 scaler 1!` | Example: `hdmi output 1 set to bypass mode` |
| `r hdmi y scaler!` | Read HDMI output scaler mode | `y=0~8`, `0` all outputs | `r hdmi 1 scaler!` | Example: `hdmi output 1 set to bypass mode` |

## EDID Commands

| Command | Description | Parameters | Example | Documented response |
| --- | --- | --- | --- | --- |
| `s edid in x from z!` | Set input EDID from a built-in, user, or copied EDID slot | `x=0~8`, `0` all inputs; `z=1~31` | `s edid in 1 from 1!` | Example: `input 1 EDID:1080p,Stereo Audio 2.0` |
| `r edid in x!` | Read input EDID assignment | `x=0~8`, `0` all inputs | `r edid in 0!` | One line per input EDID assignment |
| `r edid data hdmi y!` | Read EDID data from an HDMI output | `y=1~8` | `r edid data hdmi 1!` | Hex EDID bytes beginning with `EDID: 00 FF FF FF FF FF FF 00 ...` |

### EDID Slots

| Slot | EDID |
| --- | --- |
| `1` | `1080p,Stereo Audio 2.0` |
| `2` | `1080p,Dolby/DTS 5.1` |
| `3` | `1080p,HD Audio 7.1` |
| `4` | `1080i,Stereo Audio 2.0` |
| `5` | `1080i,Dolby/DTS 5.1` |
| `6` | `1080i,HD Audio 7.1` |
| `7` | `3D,Stereo Audio 2.0` |
| `8` | `3D,Dolby/DTS 5.1` |
| `9` | `3D,HD Audio 7.1` |
| `10` | `4K2K30_444,Stereo Audio 2.0` |
| `11` | `4K2K30_444,Dolby/DTS 5.1` |
| `12` | `4K2K30_444,HD Audio 7.1` |
| `13` | `4K2K60_420,Stereo Audio 2.0` |
| `14` | `4K2K60_420,Dolby/DTS 5.1` |
| `15` | `4K2K60_420,HD Audio 7.1` |
| `16` | `4K2K60_444,Stereo Audio 2.0` |
| `17` | `4K2K60_444,Dolby/DTS 5.1` |
| `18` | `4K2K60_444,HD Audio 7.1` |
| `19` | `4K2K60_444,Stereo Audio 2.0 HDR` |
| `20` | `4K2K60_444,Dolby/DTS 5.1 HDR` |
| `21` | `4K2K60_444,HD Audio 7.1 HDR` |
| `22` | `User1` |
| `23` | `User2` |
| `24~31` | Copy from HDMI outputs `1~8` |

## Audio Commands

| Command | Description | Parameters | Example | Documented response |
| --- | --- | --- | --- | --- |
| `s hdmi y arc z!` | Enable or disable ARC for HDMI output | `y=0~8`, `0` all outputs; `z=0~1`, `0` off, `1` on | `s hdmi 1 arc 1!` | `hdmi output 1 arc on` or off equivalent |
| `r hdmi y arc!` | Read ARC state | `y=0~8`, `0` all outputs | `r hdmi 1 arc!` | Example: `hdmi output 1 arc on` |

## CEC Commands

CEC commands send control messages to attached source or display devices.
They can power or control external devices and should be treated as side
effecting commands.

### HDMI Input CEC

For the input commands below, `x=0~8`; `0` targets all inputs.

| Command | Description | Example | Documented response style |
| --- | --- | --- | --- |
| `s cec in x on!` | Power on input device | `s cec in 1 on!` | `input 1 power on` |
| `s cec in x off!` | Power off input device | `s cec in 1 off!` | `input 1 power off` |
| `s cec in x menu!` | Send menu | `s cec in 1 menu!` | `input 1 menu` |
| `s cec in x back!` | Send back | `s cec in 1 back!` | `input 1 back` |
| `s cec in x up!` | Send up | `s cec in 1 up!` | `input 1 up` |
| `s cec in x down!` | Send down | `s cec in 1 down!` | `input 1 down` |
| `s cec in x left!` | Send left | `s cec in 1 left!` | `input 1 left` |
| `s cec in x right!` | Send right | `s cec in 1 right!` | `input 1 right` |
| `s cec in x enter!` | Send enter | `s cec in 1 enter!` | `input 1 enter` |
| `s cec in x play!` | Send play | `s cec in 1 play!` | `input 1 play` |
| `s cec in x pause!` | Send pause | `s cec in 1 pause!` | `input 1 pause` |
| `s cec in x stop!` | Send stop | `s cec in 1 stop!` | `input 1 stop` |
| `s cec in x rew!` | Send rewind | `s cec in 1 rew!` | `input 1 rewind` |
| `s cec in x ff!` | Send fast forward | `s cec in 1 ff!` | `input 1 fast forward` |
| `s cec in x previous!` | Send previous | `s cec in 1 previous!` | `input 1 previous` |
| `s cec in x next!` | Send next | `s cec in 1 next!` | `input 1 next` |
| `s cec in x mute!` | Send mute | `s cec in 1 mute!` | `input 1 mute` |
| `s cec in x vol-!` | Send volume down | `s cec in 1 vol-!` | `input 1 volume down` |
| `s cec in x vol+!` | Send volume up | `s cec in 1 vol+!` | `input 1 volume up` |

### HDMI Output CEC

For the output commands below, `y=0~8`; `0` targets all outputs.

| Command | Description | Example | Documented response style |
| --- | --- | --- | --- |
| `s cec hdmi out y on!` | Power on output display | `s cec hdmi out 1 on!` | `hdmi output 1 power on` |
| `s cec hdmi out y off!` | Power off output display | `s cec hdmi out 1 off!` | `hdmi output 1 power off` |
| `s cec hdmi out y mute!` | Send mute | `s cec hdmi out 1 mute!` | `hdmi output 1 volume mute` |
| `s cec hdmi out y vol-!` | Send volume down | `s cec hdmi out 1 vol-!` | `hdmi output 1 volume down` |
| `s cec hdmi out y vol+!` | Send volume up | `s cec hdmi out 1 vol+!` | `hdmi output 1 volume up` |
| `s cec hdmi out y active!` | Set active source | `s cec hdmi out 1 active!` | `hdmi output 1 active source` |

## Network Commands

| Command | Description | Parameters | Example | Documented response |
| --- | --- | --- | --- | --- |
| `r ipconfig!` | Read full network configuration | None | `r ipconfig!` | Includes IP mode, IP address, subnet mask, gateway, TCP/IP port, Telnet port, and MAC address |
| `r mac addr!` | Read MAC address | None | `r mac addr!` | Example: `Mac address: ...` |
| `s ip mode z!` | Set IP mode | `z=0` static, `z=1` DHCP | `s ip mode 0!` | `Set IP mode:Static`; network reboot or repower required |
| `r ip mode!` | Read IP mode | None | `r ip mode!` | Example: `IP Mode: Static` |
| `s ip addr xxx.xxx.xxx.xxx!` | Set IP address | IPv4 address | `s ip addr 192.168.1.100!` | `Set IP address:192.168.1.100`; network reboot or repower required |
| `r ip addr!` | Read IP address | None | `r ip addr!` | Example: `IP address:192.168.1.100` |
| `s subnet xxx.xxx.xxx.xxx!` | Set subnet mask | IPv4 mask | `s subnet 255.255.255.0!` | `Set subnet Mask:255.255.255.0`; network reboot or repower required |
| `r subnet!` | Read subnet mask | None | `r subnet!` | Example: `Subnet Mask:255.255.255.0` |
| `s gateway xxx.xxx.xxx.xxx!` | Set gateway | IPv4 address | `s gateway 192.168.1.1!` | `Set gateway:192.168.1.1`; network reboot or repower required |
| `r gateway!` | Read gateway | None | `r gateway!` | Example: `Gateway:192.168.1.1` |
| `s tcp/ip port x!` | Set TCP/IP port | `x=1~65535` | `s tcp/ip port 8000!` | `Set TCP/IP port:8000` |
| `r tcp/ip port!` | Read TCP/IP port | None | `r tcp/ip port!` | Example: `TCP/IP port:8000` |
| `s telnet port x!` | Set Telnet port | `x=1~65535` | `s telnet port 23!` | `Set Telnet port:23` |
| `r telnet port!` | Read Telnet port | None | `r telnet port!` | Example: `Telnet port:23` |
| `s net reboot!` | Reboot network modules | None | `s net reboot!` | Network configuration output after reboot |

TBD:

- One manual line appears to show `s network reboot!` in an example, while the
  command table and later example show `s net reboot!`. Treat `s net reboot!`
  as the documented command until verified on hardware.
- The manual includes examples using both `192.168.1.x` and `192.168.0.x`
  addresses. These are examples, not guaranteed defaults.
- The manual examples show Telnet port `10` in one network status block and
  `23` in the set/query command examples. The default Telnet port is therefore
  ambiguous until verified on hardware.

## Commands Requiring Caution

These commands are expected to have persistent, disruptive, or external side
effects and should require deliberate driver handling:

- `s reset!`: resets the unit to factory defaults.
- `s reboot!`: reboots the unit.
- `s net reboot!`: reboots network modules.
- `s power z!`: changes unit power state.
- `s hdmi y stream z!`: can disable video output streams.
- `s edid in x from z!`: changes EDID behavior observed by sources.
- `s hdmi y scaler z!`: changes output scaler behavior.
- `s hdmi y arc z!`: changes ARC behavior.
- `s save preset z!`, `s recall preset z!`, and `s clear preset z!`: change or
  apply preset state.
- `s logo1 ****************!` and `s logo2 ****************!`: change LCD text.
- `s baud rate xxx!`: changes serial transport settings.
- `s id z!`: changes the control ID.
- Network setters: `s ip mode z!`, `s ip addr xxx.xxx.xxx.xxx!`,
  `s subnet xxx.xxx.xxx.xxx!`, `s gateway xxx.xxx.xxx.xxx!`,
  `s tcp/ip port x!`, and `s telnet port x!`.
- CEC commands: may control attached source or display devices.
