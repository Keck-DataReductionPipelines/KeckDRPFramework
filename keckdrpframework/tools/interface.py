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
from keckdrpframework.utils.drpf_logger import DRPFLogger


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

    def next_event(self):
        if self._get_queue():
            try:
                return self.queue.head()
            except:
                self.queue = None
        return None

    def pending_events(self):
        if self._get_queue():
            try:
                return self.queue.get_pending()
            except:
                self.queue = None
        return None

    def in_progress_events(self):
        if self._get_queue():
            try:
                return self.queue.get_in_progress()
            except:
                self.queue = None
        return None

    def add_event(self, event):
        if self._get_queue():
            try:
                return self.queue.put(event)
            except:
                self.queue = None
        return None

    def is_queue_ok(self):
        return self.queue is not None
