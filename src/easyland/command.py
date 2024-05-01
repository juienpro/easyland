import subprocess
import json
import os
import time
import threading
from easyland.log import logger

class Command():

    def __init__(self):
        pass

    def sway_get_all_monitors(self):
        monitors = self.exec("swaymsg -t get_outputs", decode_json = True)
        return monitors
    
    def sway_get_monitor(self, name = None, make = None, model = None):
        monitors = self.sway_get_all_monitors()
        for monitor in monitors:
            if name is not None:
                if name in monitor['name']:
                    return monitor

            if make is not None:
                if make in monitor['make']:
                    return monitor

            if model is not None:
                if model in monitor['model']:
                    return monitor
        return None

    def hyprland_get_all_monitors(self):
        monitors = self.exec("hyprctl -j monitors", decode_json = True)
        return monitors
    
    def hyprland_get_monitor(self, name = None, description = None, make = None, model = None):
        monitors = self.hyprland_get_all_monitors()

        for monitor in monitors:
            if name is not None:
                if name in monitor['name']:
                    return monitor

            if description is not None:
                if description in monitor['description']:
                    return monitor

            if make is not None:
                if make in monitor['make']:
                    return monitor

            if model is not None:
                if model in monitor['model']:
                    return monitor
        return None

    def exec(self, command, background = False, decode_json = False):
        if background:
            logger.info("Executing background command: "+command)
            with open(os.devnull, 'w') as fp:
                subprocess.Popen(command, shell=True, stdout=fp)
            return True
        else:
            logger.info("Executing command: "+command) 
            output = subprocess.check_output(command, shell=True)
            decoded_output = output.decode("utf-8")
            if decode_json:
                try:
                    json_output = json.loads(decoded_output)
                except json.decoder.JSONDecodeError:
                    return None
                return json_output
            else:
                return decoded_output



