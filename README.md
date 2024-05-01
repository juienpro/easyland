# Easyland

**Easyland** is a Python framework to manage your wayland compositor (Hyprland, Sway) configuration by reacting to events. With **Easyland**, you can dismiss many side tools like Kanshi, hypridle, swayidle, etc. and script your environment according to your preferences.


## Available listeners

- [Hyprland IPC](https://wiki.hyprland.org/IPC/) event list
- [Sway IPC]( https://man.archlinux.org/man/sway-ipc.7.en)
- Systemd signals
- Native Wayland Idle system (ext_idle_notify_v1)

The tool allows to listen for these events and to execute commands in response.

## Why this tool? 

Good question.

Initially, I was a bit stressed by the number of tools needed with Hyprland (Kanshi & hypridle notably), and also by the number of bugs despite the awesome efforts of the developers. 

I wanted to have a deeper control on my system, and to be able to script it as I wanted. 

To give an example, my laptop screen brightness was always at 100% when I undock it, and Kanshi does not allow to add shell commands. This is only one small example of the numerous limitations I met during my setup of Hyprland.

By scripting my Desktop in Python, I have more control to implement what I want.

## Installation

This program needs the following external tools: 
- The `socat` binary ([Arch](https://archlinux.org/packages/extra/x86_64/socat/))
- The `gdbus` binary ([Arch](https://archlinux.org/packages/core/x86_64/glib2/))


Depending if you use Hyprland or Sway, you will need `hyprctl` or `swaymsg`.

If it's not done automatically, before using PyWayland, you will need to execute `pywayland.scanner` to generate all protocols:

```
python -m pywayland.scanner
```

or

```
pywayland-scanner
```

## How to use

The **easyland** package provides the `easyland` CLI command, which loads your custom Python file configuration with the -c parameter:

```
easyland -c ~/home/.config/hyprland/myconfig.py
```

Where `myconfig.py` contains such a content, explained in details below:

```
from easyland import logger, command

###############################################################################
# Set active listeners
###############################################################################

listeners = ['hyprland', 'systemd_logind', 'idle']

def init():
    set_monitors()

###############################################################################
# Idle configuration
# Format: [timeout in seconds, [commands to run], [commands to run on resume]]
###############################################################################

def idle_config():
    return [
        [150, ['brightnessctl -s set 0'], ['brightnessctl -r']],
        [600, ['pidof hyprlock || hyprlock']],
        [720, ['hyprctl dispatch dpms off'], ['hyprctl dispatch dpms on']]
    ]

###############################################################################
# Handler of Hyprland IPC events
# List of events: https://wiki.hyprland.org/IPC/
###############################################################################

def on_hyprland_event(event, argument):
    if event in [ "monitoradded", "monitorremoved" ]:
        logger.info('Handling hyprland event: ' + event)
        set_monitors()

###############################################################################
# Handlers of Systemd logind eventz
###############################################################################

def on_PrepareForSleep(payload):
    if 'true' in payload:
        logger.info("Locking the screen before suspend")
        command.exec("pidof hyprlock || hyprlock", True)

# To use this handler, you need to launch your locker (hyprlock or swaylock) like this: hyprlock && loginctl unlock-session
# def on_Unlock():
#     logger.info("Unlocking the screen")

# To use this handler, you need to launch your locker like this: loginctl lock-session
# def on_lock():
#     logger.info("Locking the screen")

###############################################################################
# Various methods
###############################################################################

def set_monitors():
    logger.info('Setting monitors')
    if command.hyprland_get_monitor(description="HP 22es") is not None:
        command.exec('hyprctl keyword monitor "eDP-1,preferred,auto,2"')
        # command.exec('hyprctl keyword monitor "eDP-1,disable"')
    else:
        command.exec('hyprctl keyword monitor "eDP-1,preferred,auto,2"')
        command.exec("brightnessctl -s set 0")
```

### Example of configuration 

You can find an example in the `config_examples` folder. We'll explain step-by-step the configuration called `Hyprland.py`.


#### Importing helpers

```
from easyland import logger, command
```

Easyland has helper tools to log everything (console and file) and execute commands. Just import the two. 

#### Configure listeners

```
listeners = ['hyprland', 'systemd_logind', 'idle']
```

The listeners to launch at the startup. There are currently three listeners: 
- `hyprland` to listen Hyprland IPC events
- `systemd_logind` to monitor for Systemd Logind events
- `idle` which allows you to react when your computer has no activity


#### Configure Idling

```
def idle_config():
    return [
        [150, ['brightnessctl -s set 0'], ['brightnessctl -r']],
        [600, ['pidof hyprlock || hyprlock']],
        [720, ['hyprctl dispatch dpms off'], ['hyprctl dispatch dpms on']]
    ]
```
This method configure the Idle part. It should return the list of your idle actions. Each action has three parameters:

- The timeout in seconds
- The list of commands to execute when the timeout occurs
- The optional list of commands when the timeout is resumed (eg. once there is user activity after the timeout)

Here, at 720 seconds, the screens are turned off. Then, if some activities are detected, they are turned on. 


#### Configure monitors 

```
def on_hyprland_event(event, argument):
    if event in [ "monitoradded", "monitorremoved" ]:
        logger.info('Handling hyprland event: ' + event)
        set_monitors()
```
The method `on_hyprland_event` allows you to handle Hyprland IPC events. All events are avalable [here](https://wiki.hyprland.org/IPC/).

In this case, when we connect or disconnect a monitor, we call a method to set our monitors according to our preferences. This method is as follows. 

```
def set_monitors(self):
    logger.info('Setting monitors')
    if command.hyprland_get_monitor(description="HP 22es") is not None:
        command.exec('hyprctl keyword monitor "eDP-1,disable"')
    else:
        command.exec('hyprctl keyword monitor "eDP-1,preferred,auto,2"')
        command.exec("brightnessctl -s set 0")
```
We use the `hyprland_get_monitor` command helper to get the configuration of a particular monitor. `hyprland_get_monitor` accepts the name of the monitor, its description, the maker or the model. If the screen is not found, this method returns None. 

So, when we detect a "HP 22es" monitor, we disable the screen of the laptop. Otherwise, we turn on the monitor of the laptop, and we put the brightness at the lowest level (in my configuration, when I undock my laptop, the brightness is at 100%)

For Sway, you have the `sway_get_monitor` helper method.

#### Configure suspend

```
def on_PrepareForSleep(payload):
    if 'true' in payload:
        logger.info("Locking the screen before suspend")
        command.exec("pidof hyprlock || hyprlock", True)
```

The methods `on_Whatever(payload)` are automatically called when the signal **Whatever** is sent by Systemd Logind. Here, we are listening for the signal "PrepareForSleep" which is called just before you computer is suspending.  

The second parameter of the `command.exec` helper allows you to execute a command in the background. It's necessary here, otherwhise Easyland will wait indefinitely until the screen is unlocked. 


#### Other tricks

You may be interested to listen for Lock and Unlock events emitted from Systemd when you call `loginctl lock-session` and `loginctl unlock-session`. However, keep in mind that `hyprlock` and `swaylock` do not send any signal for these events, so you need to hack that.

```
# To use this handler, you need to launch your locker (hyprlock or swaylock) like this: hyprlock && loginctl unlock-session
def on_Unlock():
    logger.info("Unlocking the screen")
```

To receive the Systemd `Unlock` signal, you should launch your screen locker with the following command: `hyprlock && loginctl unlock-session`, so Systemd will launch the `Unlock` signal when the screen is unlocked.

For locking, keep in mind that `hyprlock` and `swaylock` do not listen for the Systemd `Lock` event, so you need to it manually. 

```
# To use this handler, you need to launch your locker like this: loginctl lock-session
def on_Lock():
     logger.info("Locking the screen")
     command.exec('pidof hyprlock || hyprlock', True)
     # Do other actions if needed
```

#### Alternative to on_WhateverSignal method

Alternatively to write several methods to listen for Systemd events, you can also define method `on_systemd_event` and test the signal to achieve what you want:

```
def on_systemd_event(sender, signal, payload)
    if signal == 'Lock':
        ...
    if signal == 'PrepareForSleep':
        ...
```

## References

### Listeners handler methods


| Sender            | Handler method to add to your class | Arguments                               |
|-------------------|-------------------------------------|---------------------------------------- |
| Hyprland          | on_hyprland_event                   | event, argument                        |
| Sway              | on_sway_event_[type]                   | payload                        |
| Systemd Logind    | on_systemd_event                    | sender, signal, payload                       |
| Systemd Logind     | on_[signal]                         | payload                                    |


#### Hyprland events 

They are well documented [here](https://wiki.hyprland.org/IPC/). 

#### Sway event types

For Sway, the current event types are those defined in the [IPC manual](https://man.archlinux.org/man/sway-ipc.7.en)

#### Systemd Logind events

These events are called "signals" in the Systemd terminology. 

They are not well documented but you can try to [read that](https://www.freedesktop.org/software/systemd/man/latest/org.freedesktop.login1.html) (good luck). 

Some examples that can be useful:

| Member | Description  |
|------- |-------------------------------------------------------------------|
| PrepareForShutdown | Sent before a shutdown |
| PrepareForSleep | Sent before suspend |
| Lock | Sent when a lock is requested, eg `loginctrl lock-session` |
| Unlock | Sent when an unlock is requested | 
| SessionNew | When a session is created |

Keep in mind that these signals are independent from Wayland/Hyprland/Sway. My recommendation would be to always configure your compositor to use loginctl to send the signals, and add a listener in **Easyland** to achieve what you want.

#### Available helpers

| Method | Usage | Arguments |
|--------|-------|-----------|
| command.exec | Execute a command, eventually in the background | cmd (string), background (bool, default False), decode_json (bool, default False) |
| command.hyprland_get_all_monitors | Get all monitors and their configuration through Hyprland IPC | None |
| command.hyprland_get_monitor | Get the config of one monitor, None if not found | name, description, make, model |
| command.sway_get_all_monitors | Get all monitors and their configuration through Hyprland IPC | None |
| command.sway_get_monitor | Get the config of one monitor, None if not found | name, make, model |
| logger | Log messages to easyland.log and to STDOUT | use logger.info, logger.error, for the severity etc. |
| idle_config | Set the idle configuration | None


## Contributions

- Integrating other DBUS services should be easy with Easyland (type `dbusctl` to list all avalable DBUS on your system). Do not hesitate to let know what you need.
- Better tests for Sway. I use Hyprland so feel free to submit bugs if you are using Sway

If you see some bugs or propose patches, feel free to contribute.


## Thanks

Thanks to the developer(s) of [Hyprland](https://hyprland.org) for their fantastic compositor. I tried so many ones in the past, and this has been Hyprland that convinced me to do the switch from KDE :-)




