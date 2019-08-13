'''
Created on Jul 8, 2019

@author: shkwok
'''

from keckdrpframework.models.event import Event
from keckdrpframework.models.data_set import Data_set


class Processing_context:
    '''
    classdocs
    '''

    def __init__(self, event_queue_hi, logger, config):
        '''
        Constructor
        '''
        self.name = 'Processing_context'
        self.state = 'Undefined'
        self.event_queue_hi = event_queue_hi
        self.logger = logger
        self.config = config
        self.data_set = Data_set (None, logger, config)
        #self.bokeh_session = bokeh_session
        
    def push_event (self, name, args):
        self.event_queue_hi.put(Event (name, args))
