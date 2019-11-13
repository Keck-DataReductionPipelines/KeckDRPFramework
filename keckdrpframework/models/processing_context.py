"""
Created on Jul 8, 2019

@author: skwok
"""

from keckdrpframework.models.event import Event
from keckdrpframework.models.data_set import Data_set


class Processing_context:
    """
    The
    """

    def __init__(self, event_queue, event_queue_hi, logger, config):
        """
        The context is a container for data needed for the pipeline.
        It is passed along as parameter in each method call in the pipeline class.
        """
        self.name = "Processing_context"
        self.state = "Undefined"
        self.event_queue_hi = event_queue_hi
        self.event_queue = event_queue
        self.logger = logger
        self.config = config
        self.data_set = Data_set(None, logger, config)
        self.debug = False
        
    def push_event (self, event_name, args):
        self.event_queue_hi.put(Event (event_name, args))
