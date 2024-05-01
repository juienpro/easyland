import subprocess
import threading
import re
import time
import json
import sys
from easyland.log import logger
from easyland.idle import Idle

class Daemon():

    def __init__(self, config):
        self.config = config 
        listeners = self.get_listeners()
        logger.info('Starting easyland daemon')

        if 'hyprland' in listeners:
            hyprland_thread = threading.Thread(target=self.launch_hyprland_daemon)
            hyprland_thread.daemon = True
            hyprland_thread.start()

        if 'sway' in listeners: 
            if not hasattr(self.config, 'sway_event_types'):
                logger.error('No sway event types defined for Sway listeners in the config file')
                sys.exit(1)
            existing_types = ['workspace', 'window', 'output', 'mode', 'barconfig_update', 'binding', 'shutdown', 'tick', 'bar_state_update', 'input']
            sway_threads = [None] * len(self.config.sway_event_types)
            for idx, event_type in enumerate(self.config.sway_event_types):
                if event_type not in existing_types:
                    logger.error('Sway - Invalid event type: ' + event_type)
                    sys.exit(1)
                sway_threads[idx] = threading.Thread(target=self.launch_sway_daemon, args=(event_type,)) 
                sway_threads[idx].daemon = True
                sway_threads[idx].start()

        if 'systemd_logind' in listeners:
            systemd_thread = threading.Thread(target=self.launch_systemd_login_daemon)
            systemd_thread.daemon = True
            systemd_thread.start()

        if 'idle' in listeners:
            if callable(getattr(self.config, 'idle_config', None)):
                idle_thread = threading.Thread(target=self.launch_idle_daemon)
                idle_thread.daemon = True
                idle_thread.start()

        self.call_handler('init')

    def get_listeners(self):
        if hasattr(self.config, 'listeners'):
            return self.config.listeners
        else:
            logger.error('No listeners defined in the config file')
            sys.exit(1)


    def call_handler(self, handler, *argv): 
        func = getattr(self.config, handler, None)
        if callable(func):
            func(*argv)
    
    def launch_idle_daemon(self):
        idle_config = self.config.idle_config()
        idle = Idle(idle_config)
        idle.setup()

    def launch_hyprland_daemon(self):
        logger.info('Launching hyprland daemon')
        cmd = "socat -U - UNIX-CONNECT:/tmp/hypr/$HYPRLAND_INSTANCE_SIGNATURE/.socket2.sock"
        ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        while True:
            for line in iter(ps.stdout.readline, ""):
                self.last_event_time = time.time()
                decoded_line = line.decode("utf-8")
                if '>>' in decoded_line:
                    data = decoded_line.split('>>')
                    self.call_handler('on_hyprland_event', data[0], data[1])

    def launch_sway_daemon(self, event_type):
        logger.info('Launching Sway daemon for event type: ' + event_type)
        cmd = "swaymsg -m -r -t subscribe '[\"" + event_type + "\"]'"
        ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        while True:
            for line in iter(ps.stdout.readline, ""):
                decoded_line = line.decode("utf-8").strip()
                try:
                    json_output = json.loads(decoded_line)
                    self.call_handler('on_sway_event_' + event_type, json_output)
                except json.decoder.JSONDecodeError:
                    logger.error('Sway daemon: Invalid JSON: '+ decoded_line)

    def launch_systemd_login_daemon(self):
        logger.info('Launching systemd daemon')
        cmd = "gdbus monitor --system --dest org.freedesktop.login1"
        ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        while True:
            for line in iter(ps.stdout.readline, ""):
                decoded_line = line.decode("utf-8").strip()
                res = re.match(r'(.+?): ([^\s]+?) \((.*?)\)$', decoded_line)
                if res:
                    sender = res.group(1)
                    name = res.group(2)
                    payload = res.group(3)

                    if 'Properties' not in name:
                        signal_name = name.split('.')[-1]
                        f = 'on_' + signal_name 
                        self.call_handler(f, payload)
                        self.call_handler('on_systemd_event', sender, signal_name, payload)
   

