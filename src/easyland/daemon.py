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
        self.listeners = self.get_listeners()
        listener_names = self.listeners.keys()

        logger.info('Starting easyland daemon')

        if 'hyprland' in listener_names:
            hyprland_thread = threading.Thread(target=self.launch_hyprland_daemon)
            hyprland_thread.daemon = True
            hyprland_thread.start()

        if 'sway' in listener_names: 
            if not 'event_types' in self.listeners['sway']:
                logger.error('No sway event types defined for Sway listeners in the config file')
                sys.exit(1)
            existing_types = ['workspace', 'window', 'output', 'mode', 'barconfig_update', 'binding', 'shutdown', 'tick', 'bar_state_update', 'input']
            sway_threads = [None] * len(self.listeners['sway']['event_types'])
            for idx, event_type in enumerate(self.listeners['sway']['event_types']):
                if event_type not in existing_types:
                    logger.error('Sway - Invalid event type: ' + event_type)
                    sys.exit(1)
                sway_threads[idx] = threading.Thread(target=self.launch_sway_daemon, args=(event_type,)) 
                sway_threads[idx].daemon = True
                sway_threads[idx].start()

        if 'systemd_logind' in listener_names:
            systemd_thread = threading.Thread(target=self.launch_systemd_login_daemon)
            systemd_thread.daemon = True
            systemd_thread.start()

        if 'idle' in listener_names:
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
        socket = self.listeners['hyprland'].get('socket_path', '$XDG_RUNTIME_DIR/hypr/$HYPRLAND_INSTANCE_SIGNATURE/.socket2.sock')
        cmd = "socat -U - UNIX-CONNECT:"+socket
        # ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        while True:
            if ps.returncode != 0:
                err = ps.stderr.read().decode("utf-8")
                logger.error("Error while listening to Hyprland socket: " + err)
                sys.exit(1)
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
                    logger.error('Sway daemon: Exiting')
                    return

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
   

