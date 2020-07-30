"""
Created on Jul 8, 2019

@author: skwok
"""

from keckdrpframework.models.event import Event
from keckdrpframework.models.data_set import DataSet


class ProcessingContext:
    """
    The processing context is a place holder for all objects that 
    are needed or created during processing.
    """

    def __init__(self, event_queue, event_queue_hi, logger, config):
        """
        The context is a container for data needed for the pipeline.
        It is passed along as parameter in each method called in the pipeline class.
        """
        self.name = "Processing_context"
        self.state = "Undefined"
        self.event_queue_hi = event_queue_hi
        self.event_queue = event_queue
        self.logger = logger
        self.config = config
        self.data_set = None
        self.debug = False

    def push_hi_event(self, event_name, args):
        """
        Creates a new event and appends it to the high priority event queue.
        The high priority queue is local to the current process.
        The new event is not recurrent.
        """
        self.event_queue_hi.put(Event(event_name, args, recurrent=False))

    def push_event(self, event_name, args):
        """
        Deprecated use push_hi_event instead
        """
        self.push_hi_event(event_name, args)

    def append_event(self, event_name, args, recurrent=False):
        """
        Creates a new event and appends it to the low priority event queue.
        The low priority queue is local to the current process.
        """
        self.event_queue.put(Event(event_name, args, recurrent=recurrent))
