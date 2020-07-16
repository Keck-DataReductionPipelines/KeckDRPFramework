import sys
import os


def import_module(mod_name):
    """
    Traverse the full path of this file to find the desired module name.
    Then import that desired module.

    For example:        
        from toolHelper import import_module
        import_module ("keckdrpframework")

    """
    realpath = os.path.realpath(__file__)
    parts = realpath.split(os.path.sep)
    for i, p in enumerate(parts):
        if p == mod_name:
            sys.path.append(os.path.sep.join(parts[:i]))
            break


import_module("keckdrpframework")

from keckdrpframework.models.event import Event
from keckdrpframework.models.arguments import Arguments
from keckdrpframework.core import queues
from keckdrpframework.core.framework import Framework
from keckdrpframework.config.framework_config import ConfigClass
from keckdrpframework.models.processing_context import ProcessingContext
from keckdrpframework.utils.drpf_logger import DRPFLogger, getLogger


class FrameworkInterface:
    def __init__(self, cfg=None):
        self.config = cfg if cfg is not None else ConfigClass()
        self.queue = None
        self._get_queue()

    def _get_queue(self):
        """
        Returns True is getting event queue was successful.
        """
        if self.queue is None:
            cfg = self.config
            hostname = cfg.queue_manager_hostname
            portnr = cfg.queue_manager_portnr
            auth_code = cfg.queue_manager_auth_code
            self.queue = queues.get_event_queue(hostname, portnr, auth_code)
        return self.queue is not None

    def start_event_queue(self):
        """
        Starts a queue manager, if queue is None.
        Returns the queue.
        """
        q_ok = self._get_queue()
        if not q_ok:
            cfg = self.config
            hostname = cfg.queue_manager_hostname
            portnr = cfg.queue_manager_portnr
            auth_code = cfg.queue_manager_auth_code
            queues.start_queue_manager(hostname, portnr, auth_code, logger=None)
            return self._get_queue()
        return q_ok

    def stop_event_queue(self):
        """
        Tells the queue manager process to terminate.
        Returns True if successful.
        """
        if self.queue is None:
            return
        try:
            self.queue.terminate()
        except:
            # Once the quueue manager terminates, there will be an exception.
            # Just ignore it.
            pass
        self.queue = None
        return

    def next_event(self):
        """
        Gets the head of the event queue.
        Returns an event or None
        """
        if self._get_queue():
            try:
                return self.queue.head()
            except:
                self.queue = None
        return None

    def pending_events(self):
        """
        Returns a copy of the event queue, an empty tuple or None.
        """
        if self._get_queue():
            try:
                res = self.queue.get_pending()
                if res is None:
                    return tuple()
                else:
                    return res
            except Exception as e:
                print("pending", e)
                self.queue = None
        return None

    def in_progress_events(self):
        """
        Returns the in_progress dict, an empty dict or None
        """
        if self._get_queue():
            try:
                res = self.queue.get_in_progress()
                if res is None:
                    return dict()
                else:
                    return res
            except:
                self.queue = None
        return None

    def add_event(self, event):
        """
        Addes new event to the queue
        """
        if self._get_queue():
            try:
                return self.queue.put(event)
            except:
                self.queue = None
        return None

    def is_queue_ok(self):
        return self.queue is not None
