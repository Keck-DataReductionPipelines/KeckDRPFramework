"""
Created on Jul 8, 2019

This module implements the event queue interface.
In the first version, the queue is simply the Python queue.Queue.

Python Queue is thread safe, but limited to a single process.


The current implementation uses a Manager process, multiprocessing.Manager(), which allows sharing of objects over a network.
The access is shared by using a proxy. A shared Queue() can be created as a proxy object.

If multi-processing is desired, as defined in config.want_multiprocessing, then the queue-manager process must be started first.
This queue-manager process will not do anything processing.
The consumers/client processes can then connect to the queue-manager process.

To start a group of processes on multiple hosts, the only requirements is that the 
queue manager server process is started first. The clients can use the same configuration file
and run on same or different hosts. 

Possible alternatives:
------------
Multiprocessing Queue from the module multiprocessing.Queue.
This method is limited to run in a single host.

Implementation using a database (ie. MySql), where a queue is a table in the database.
Multiple processes can share the access to that queue even from different hosts.

Shared objects must be 'picklable'.  

@author: skwok
"""

import os
import queue
import time
import traceback
from multiprocessing.managers import BaseManager
from multiprocessing import Process


class SimpleEventQueue(queue.Queue):
    """
    Just subclass queue.Queue
    Operations are get() and put()
    """

    def __init__(self, *args, **kargs):
        """
        Constructor
        """
        queue.Queue.__init__(self, *args)

    def get_pending(self):
        """
        Returns a copy of the queue's content
        """
        return list(self.queue)


class MultiprocEventQueue:
    """
    This is also a simple queue. 
    This is instantiated when the proxy server is started.
    Clients/consumers should call get_queue() to get the proxy of the queue.
    """

    def __init__(self):
        self.queue = queue.Queue()

    def put(self, value):
        self.queue.put(value)

    def get(self, block=True, timeout=0):
        return self.queue.get(block=block, timeout=timeout)

    def qsize(self):
        return self.queue.qsize()

    def terminate(self):
        os._exit(0)


class QueueServer(BaseManager):
    pass


def _get_queue_manager(hostname, portnr, auth_code):
    try:
        QueueServer.register("get_queue")
        manager = QueueServer(address=(hostname, portnr), authkey=auth_code)
        manager.connect()
        return manager
    except Exception as e:
        return None


def _queue_manager_target(hostname, portnr, auth_code):
    """
    Starts the proxy queue manager process.
    This should be spawn as a process and run in the background.  
    """
    try:
        queue = MultiprocEventQueue()
        QueueServer.register("get_queue", callable=lambda: queue)

        manager = QueueServer(address=(hostname, portnr), authkey=auth_code)
        server = manager.get_server()
        server.serve_forever()
    except Exception as e:
        print(e, hostname, portnr, auth_code)

    print("Queue manager target terminated")


def start_queue_manager(hostname, portnr, auth_code):
    p = Process(target=_queue_manager_target, args=(hostname, portnr, auth_code))
    p.start()
    time.sleep(2)
    return p


def get_event_queue(hostname, portnr, auth_code):
    """
    This functions gets the shared queue.
    First it connects to the manager, the process that contains the queue.
    Then it asks the manager for the queue by calling the registered function get_queue(). 
    """
    manager = _get_queue_manager(hostname, portnr, auth_code)
    if manager is None:
        return None
    return manager.get_queue()
