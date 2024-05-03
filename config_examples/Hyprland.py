from easyland import logger, command

###############################################################################
# Set active listeners
###############################################################################

listeners = ['hyprland', 'systemd_logind', 'idle']

listeners = {
    "hyprland": { "socket_path": "/tmp/hypr/$HYPRLAND_INSTANCE_SIGNATURE/.socket2.sock" },
    'systemd_logind': {},
    'idle': {}
}

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
        # command.exec('hyprctl keyword monitor "eDP-1,preferred,auto,2"')
        command.exec('hyprctl keyword monitor "eDP-1,disable"')
    else:
        command.exec('hyprctl keyword monitor "eDP-1,preferred,auto,2"')
        command.exec("brightnessctl -s set 0")

