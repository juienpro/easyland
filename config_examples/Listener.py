from easyland import logger


listeners = ['hyprland', 'systemd_logind', 'idle']


def idle_config():
    return [
        [5, ['echo "Entering Idle"'], ['echo "Resuming Idle"']],
    ]

def on_hyprland_event(event, argument):
    logger.info("Hyprland: Receveid '"+event +"' with argument "+argument.strip())        


def on_systemd_event(sender, signal, payload):
    logger.info("Systemd: Received from '"+sender+"': "+ signal +' with payload: '+payload)
