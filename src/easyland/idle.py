# import .command as Command 
from . import command
from . import logger
import subprocess
import threading
import os
from pywayland.client import Display
from pywayland.protocol.wayland.wl_seat import WlSeat
from pywayland.protocol.ext_idle_notify_v1 import (
    ExtIdleNotificationV1,
    ExtIdleNotifierV1
)

class Idle():
    def __init__(self, config):
        # self.command = Command.Command()
        self.command = command
        self._config = config
        self._display =  Display()
        self._display.connect()
        self._idle_notifier = None
        self._seat = None
        self._notifications = []

    def _global_handler(self, reg, id_num, iface_name, version):
        if iface_name == 'wl_seat':
            self._seat = reg.bind(id_num, WlSeat, version)

        elif iface_name == "ext_idle_notifier_v1":
            self._idle_notifier = reg.bind(id_num, ExtIdleNotifierV1, version)
    
            for idx, c in enumerate(self._config):
                self._notifications.append(None)
                self._notifications[idx] = self._idle_notifier.get_idle_notification(c[0] * 1000, self._seat)
                self._notifications[idx]._index = idx
                self._notifications[idx].dispatcher['idled'] = self._idle_notifier_handler
                self._notifications[idx].dispatcher['resumed'] = self._idle_notifier_resume_handler

    def _idle_notifier_handler(self, notification): 
        for command in self._config[notification._index][1]:
            logger.info('Idle - Running command: ' + command)
            with open(os.devnull, 'w') as fp:
                subprocess.Popen(command, shell=True, stdout=fp)

    def _idle_notifier_resume_handler(self, notification):
        if len(self._config[notification._index]) > 2:
            for command in self._config[notification._index][2]:
                logger.info('Idle - Resuming: Running command: ' + command)
                with open(os.devnull, 'w') as fp:
                    subprocess.Popen(command, shell=True, stdout=fp)

    def setup(self):
        reg = self._display.get_registry()
        reg.dispatcher['global'] = self._global_handler
        while True:
            self._display.dispatch(block=True)


