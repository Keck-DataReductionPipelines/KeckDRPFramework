"""
Start Queue Manager

Created on 2020-01-07

@author skwok
"""

import sys
import argparse
import socket
import os
import logging

from interface import import_module

import_module("keckdrpframework")

from keckdrpframework.core import queues
from keckdrpframework.config.framework_config import ConfigClass


def _parseArguments(in_args):
    description = "Start event queue manager"
    usage = "\n{} config_file\n".format(in_args[0])
    epilog = "\nStart event queue manager\n"

    parser = argparse.ArgumentParser(prog=f"{in_args[0]}", description=description, usage=usage, epilog=epilog)
    parser.add_argument("-c", "--config", dest="config_file", type=str, help="Configuration file")
    parser.add_argument("-H", "--host", dest="hostname", type=str, help="Host name")
    parser.add_argument("-p", "--port", dest="portnr", type=str, help="Port number")

    try:
        return parser.parse_args(in_args[1:])
    except:
        # parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    args = _parseArguments(sys.argv)
    cfg = ConfigClass(args.config_file)
    cfg.properties["want_multiprocessing"] = True
    hostname = cfg.queue_manager_hostname if args.hostname is None else args.hostname
    portnr = cfg.queue_manager_portnr if args.portnr is None else args.portnr
    auth_code = cfg.queue_manager_auth_code

    if queues.get_event_queue(hostname, portnr, auth_code) is not None:
        print("Queue Manager is already running\n")
    else:
        queue = queues.start_queue_manager(hostname, portnr, auth_code, logger=logging.getLogger())

        print(f"Hostname = {hostname}\nPort nr = {portnr}\n")
        print("Started Queue Manager.")
    os._exit(0)
