"""
Created on Jul 8, 2019

@author: shkwok
"""

import queue

class Event_queue (queue.Queue):  
    def __init__(self, *args, **kargs):
        """
        Constructor
        """
        queue.Queue.__init__(self, *args)        
        
        
    def get_pending (self):
        """
        Returns a copy of the queue's content
        """
        return list (self.queue)