#!/usr/bin/env python3
import argparse
import importlib
import importlib.util
import importlib.machinery
import sys
import time
import os
from easyland.daemon import Daemon

version = '0.7.1'

def import_from_path(path):
    module_name = os.path.basename(path).replace('-', '_').replace('.py', '')
    spec = importlib.util.spec_from_loader(module_name, importlib.machinery.SourceFileLoader(module_name, path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules[module_name] = module
    return module

def main():

    parser = argparse.ArgumentParser(description="Easyland - A python swiss-knife to manage Wayland compositors like Hyprland and Sway")
    parser.add_argument("-c", "--config", help="Path to your config file")
    parser.add_argument("-v", "--version", action="store_true", help="Show the version")
    args = parser.parse_args()

    if args.version:
        print('Pyland version: ' + version)
        sys.exit()

    if not args.config:
        print('Please provide a config file with the option -c')
        sys.exit(1)

    config = import_from_path(args.config)
    daemon = Daemon(config)
    while True:
        time.sleep(1)

if __name__ == '__main__':
    main()
