
## v0.7.6  (2024-05-15) 

- Major fix: Idle thread launched several times leading to unexpected events
- Minor fix: Improvement of the Hyprland config example to restart waybar and wpaperd each time the monitors change
- Minor fix: Versionning

## v0.7.5  (2024-05-13) 

- Fix Hyprland socket path (support of Hyprland v0.4)
- Better errors management in Hyprland IPC thread

## v0.7.4  (2024-05-13) 

- Fix Wayland dispatcher 

## v0.7.3  (2024-05-13) 

- Fix listeners of Hyprland.py

## v0.7.2  (2024-05-03) 

- Added the possibility to change the path of the Hyprland socket
- Better parameters definition for Listeners
- Minor changes

## v0.7.1  (2024-05-02) 

- Minor changes (docs and config examples)

## v0.7.0 (2024-05-02) 

- Full rewrite
- Implementation of a real Wayland Idle system

## v0.6 (2024-04-26) 

- Added support for background shell commands by adding & at the end of the command. Should fix the issue with hyprlock that blocks a thread.
- Rename CHANGELOG.txt to CHANGELOG.md

## v0.5 (2024-04-26) 

- Added the parent class `Config.py` to each user-config class, to make user-defined class easier 
- Added the possibility to configure idle actions easily with `set_idle_config` and `do_idle_with_config` methods.  

## v0.4 (2024-04-26) 

- Added Changelog.txt

## v0.3 (2024-04-26) 

- DBUS monitoring is made with `gdbus` instead of `dbus-monitor`. Indeed, `gdbus` displays received messages on a single line, including the payload, which ease the parsing.
- Includes the payload in Systemd handler functions
- Added version number to the script

## v0.2 (2024-04-26) 

- Updated myConfig to fix a bug in the Idle handler 

## v0.1 (2024-04-25) 

- Initial Release
