"""
Event queue info

Created on 2020-01-07

@author skwok
"""

import sys
import argparse
import socket

from interface import import_module

import_module("keckdrpframework")

from keckdrpframework.core import queues
from keckdrpframework.config.framework_config import ConfigClass


def _parseArguments(in_args):
    description = "Get event queue info"
    usage = "\n{} [config_file]\n".format(in_args[0])
    epilog = "\nGet event queue info\n"

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

    queue = queues.get_event_queue(hostname, portnr, auth_code)
    print("Event queue:")
    print(f"Hostname = {hostname}\nPort nr = {portnr}\n")

    if queue is None:
        print("Failed to connect to Queue Manager")
    else:
        print("Event queue size =", queue.qsize())
        pending = queue.get_pending()
        for i, elem in enumerate(pending):
            print(f"Event #{i}: {elem}")

        print("In progress:")
        in_progress = queue.get_in_progress()
        for i, (id, evt) in enumerate(in_progress.items()):
            print(f"Event #{i}: {evt.name}, {evt.args}")
