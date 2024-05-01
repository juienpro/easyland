from easyland import logger, command

listeners = ['sway', 'systemd_logind', 'idle']

sway_event_types = ['workspace', 'window']


###############################################################################
# Idle configuration
# Format: [timeout in seconds, [commands to run], [commands to run on resume]]
###############################################################################

def idle_config():
    return [
        [5, ['echo "Idle for 5 seconds"'], ['echo "Resumed"']],
        [150, ['brightnessctl -s set 0'], ['brightnessctl -r']],
        [600, ['pidof hyprlock || hyprlock']],
        [720, ['hyprctl dispatch dpms off'], ['hyprctl dispatch dpms on']]
    ]


###############################################################################
# Handler of Sway IPC events
# List of events: https://man.archlinux.org/man/sway-ipc.7.en
###############################################################################
def on_sway_event_workspace(payload):
    logger.info('Handling Sway workspace event: ' + payload['change'])

def on_sway_event_window(payload):
    logger.info('Handling Sway window event: ' + payload['change'])

###############################################################################
# Handlers of Systemd logind eventz
###############################################################################

def on_PrepareForSleep(payload):
    if 'true' in payload:
        logger.info("Locking the screen before suspend")
        command.exec("pidof swaylock || swaylock", True)

