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

Shared objects must be 'pickleable'.  

@author: skwok
"""

import os
import queue
import time
import copy
import traceback
from multiprocessing.managers import BaseManager
from multiprocessing import Process


class SimpleEventQueue:
    """
    This class represents the event queue in in both single process and multi-processing modes.
    
    The event queue is the FIFO queue, the Python standard queue.Queue().
    The framework code takes events from this queue and calls the associated action.

    The dictionary 'in_progress' contains events that are in progress.
    When an event is taken from the event queue, that event is added to in_progress.
    If the event is handled successfully, the event is removed from in_progress,
    unless it is a recurrent event. In that case, the event is re-inserted to the queue.

    Otherwise, if there is an error, the event can be re-inserted into the event queue,
    or discarded, depending on the event handler.

    This is instantiated when the proxy server is started.
    Clients/consumers should call get_queue() to get the proxy of the queue.
    """

    def __init__(self):
        self.queue = queue.Queue()
        self._in_progress = dict()

    def put(self, value):
        self.queue.put(value)

    def get(self, block=True, timeout=0):
        event = self.queue.get(block=block, timeout=timeout)
        self._in_progress[event.id] = event
        return event

    def head(self):
        """
        Returns the head of the queue.
        """
        try:
            return list(self.queue.queue)[0]
        except:
            return None

    def qsize(self):
        return self.queue.qsize()

    def terminate(self):
        os._exit(0)

    def discard(self, event_id):
        """
        Rmmoves event from in_progress list.
        """
        ev = self._in_progress.get(event_id)
        if ev is not None:
            del self._in_progress[event_id]
        return ev

    def re_append(self, event_id):
        """
        Re-appends event to the event_queue.
        """
        ev = self.discard(event_id)
        self.put(ev)

    def get_pending(self):
        """
        Returns a copy of the queue's content
        """
        return list(self.queue.queue)

    def get_in_progress(self):
        """
        Returns the in_progress dict
        """
        return self._in_progress


class QueueServer(BaseManager):
    pass


def _get_queue_manager(hostname, portnr, auth_code):
    """
    Connects to a running queue manager.
    Returns None is queue manager is not running.
    """
    try:
        QueueServer.register("get_queue")
        manager = QueueServer(address=(hostname, portnr), authkey=auth_code)
        manager.connect()
        return manager
    except Exception:
        return None


def _queue_manager_target(hostname, portnr, auth_code, logger):
    """
    This is the target method for the process that runs the queue manager.    
    This should be spawn as a process and run in the background.  
    """
    try:
        queue = SimpleEventQueue()
        QueueServer.register("get_queue", callable=lambda: queue)

        manager = QueueServer(address=(hostname, portnr), authkey=auth_code)
        server = manager.get_server()
        server.serve_forever()
    except Exception as e:
        if logger is not None:
            logger.error("Exception in _queue_manager_target: {}".format(e))

    if logger is not None:
        logger.info("Queue manager process terminated")


def start_queue_manager(hostname, portnr, auth_code, logger):
    """
    Starts the queue manager process.
    """
    p = Process(target=_queue_manager_target, args=(hostname, portnr, auth_code, logger))
    p.start()
    for i in range(10):
        time.sleep(2)
        if get_event_queue(hostname, portnr, auth_code) is not None:
            break
    else:
        logger.debug(f"Queue ready {i}")
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
