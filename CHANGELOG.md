
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
