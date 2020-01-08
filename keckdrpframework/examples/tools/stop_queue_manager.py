"""
Stop Queue Manager

Created on 2020-01-07

@author skwok
"""

import sys
import argparse
from keckdrpframework.core import queues
from keckdrpframework.config.framework_config import ConfigClass

def _parseArguments (in_args):
    description = "Stop event queue manager"
    usage = "\n{} config_file\n".format(in_args[0])
    epilog = "\nStop event queue manager\n"
    
    parser = argparse.ArgumentParser(prog=f"{in_args[0]}", description=description, usage=usage, epilog=epilog)    
    parser.add_argument (dest="config_file", type=str, help="Configuration file")
    try:
        return parser.parse_args(in_args[1:])
    except:
        parser.print_help()
        sys.exit(0)
    
if __name__ == "__main__":
    args = _parseArguments(sys.argv)
    cfg = ConfigClass (args.config_file)
    hostname = cfg.queue_manager_hostname
    portnr = cfg.queue_manager_portnr
    auth_code = cfg.queue_manager_auth_code
    queue = queues.get_event_queue(hostname, portnr, auth_code)
    print (f"Hostname = {hostname}\nPort nr = {portnr}\nAuth code = {auth_code}")
    if queue is None:
        print ("Failed to connect to Queue Manager")
    else:
        try:
            queue.terminate()
        except:
            pass
        print ("Stop request sent.")