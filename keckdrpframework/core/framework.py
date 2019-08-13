'''
Created on Jul 8, 2019

@author: skwok
'''

import datetime
import threading
import signal
import traceback
import time

from keckdrpframework.core.queues import Event_queue

# Server Task import
from keckdrpframework.core.server_task import DRPF_server_handler, start_http_server

from keckdrpframework.models.processing_context import Processing_context
from keckdrpframework.models.arguments import Arguments
from keckdrpframework.models.action import Action
from keckdrpframework.models.event import Event
from keckdrpframework.models.data_set import Data_set

from keckdrpframework.utils.DRPF_logger import getLogger

from keckdrpframework.config.framework_config import ConfigClass
from bokeh.client import push_session
from bokeh.io import curdoc
from bokeh.plotting.figure import figure
from bokeh.layouts import column
import pkg_resources



class Framework(object):
    '''
    This class implements the core of the framework.
    There are two threads: the event loop and the action loop.
    '''
    
    def __init__(self, pipeline, configFile):
        '''
        pipeline: a class containing recipes
        
        Creates the event_queue and the action queue
        '''
        self.config = ConfigClass (configFile)
        self.logger = getLogger (self.config.logger_config_file, name ="DRPF")
        pipeline.set_logger (self.logger)
        
        self.event_queue = Event_queue()
        self.event_queue_hi = Event_queue()   
        
        self.pipeline = pipeline
        self.context = Processing_context (self.event_queue_hi, self.logger, self.config)
        self.keep_going = True
        self.init_signal ()
    
    def get_event (self):
        try:
            try:
                return self.event_queue_hi.get_nowait()
            except:                                  
                return self.event_queue.get(True, self.config.event_timeout)
        except Exception as e:
            ev = self.config.no_event_event
            if ev is None:
                return None
            time.sleep(self.config.no_event_wait_time)
            ev.args = Arguments(name=ev.name, time=datetime.datetime.ctime(datetime.datetime.now()))  
            return ev

    def _push_event (self, event_name, args):
        '''
        Pushes high priority events
        
        Normal events go to the lower priority queue
        Only used in execute.
        
        '''
        self.logger.info (f"Push event {event_name}, {args.name}")
        self.event_queue_hi.put(Event (event_name, args))
        
    def append_event (self, event_name, args):
        '''
        Appends low priority event to the end of the queue
        '''                
        self.event_queue.put (Event (event_name, args))
                                   
    def event_to_action (self, event, context):
        '''
        Passes event.args to action.args
        
        Note that event.args comes from previous action.output.
        '''
        event_info = self.pipeline.event_to_action (event, context)
        self.logger.info (f'Event to action {event_info}')
        return Action (event_info, args=event.args)
    
    def execute (self, action, context):
        '''
        Executes one action
        The input for the action is in action.args.
        The action returns action_output and it is passed to the next event if action is successful.
        '''
        pipeline = self.pipeline
        action_name = action.name
        try:
            if pipeline.get_pre_action(action_name)(action, context):
                if self.config.print_trace:
                    self.logger.info ('Executing action ' + action.name)
                action_output = pipeline.get_action(action_name)(action, context)
                if pipeline.get_post_action(action_name)(action, context):
                    if not action.new_event is None:
                        new_args = Arguments() if action_output is None else action_output 
                        self._push_event (action.new_event, new_args)
                    if not action.next_state is None:
                        context.state = action.next_state
                    if self.config.print_trace:
                        self.logger.info ('Action ' + action.name + ' done')
                    return
                else:
                    # post-condition failed
                    context.state = 'stop'
            else:
                # Failed pre-condition
                if self.config.pre_condition_failed_stop:
                    context.state = 'stop'
        except:
            self.logger.error ("Exception while invoking {}. Execution stopped.".format (action_name))
            context.state = 'stop'
            if self.config.print_trace:
                traceback.print_exc()
    
    def start_action_loop (self):
        '''
        This is a thread running the action loop.
        '''

        def loop ():
            #if self.context.config.instrument.interactive >=1:

            self.context.bokeh_session = push_session(curdoc())
            p=figure()
            c=column(children=[p])
            curdoc().add_root(c)
            self.context.bokeh_session.show(c)

            while self.keep_going:
                try:    
                    action = ''
                    event = ''
                    event = self.get_event ()
                    if event is None:                        
                        self.logger.info ("No new events - do nothing")
                    
                        if self.event_queue.qsize() == 0 and \
                            self.event_queue_hi.qsize() == 0:
                            self.logger.info (f"No pending events or actions, terminating")
                            self.keep_going = False
                    else:       
                        action = self.event_to_action (event, self.context)                        
                        self.execute(action, self.context)
                    if self.context.state == 'stop':
                        break
                except Exception as e:
                    self.logger.error (f"Exception while processing action {action}, {e}")
                    if self.config.print_trace:
                        traceback.print_exc()
                    break                
            self.keep_going = False



        thr = threading.Thread (name='action_loop', target=loop)
        thr.setDaemon(True)
        thr.start()

    def init_signal (self):
        '''
        Captures keyboard interrupt
        '''

        def handler (*args):
            self.keep_going = False

        # signal.signal (signal.CTRL_BREAK_EVENT, handler)
        signal.signal (signal.SIGINT, handler)
        
    def start (self):
        '''
        Starts the event loop and the action loop
        '''  
        self.start_action_loop ()
        
    def waitForEver (self):            
        while self.keep_going:
            time.sleep (1)

    #
    # Methods for HTTP server
    #
    def http_server_loop (self):        
        start_http_server(self, self.config, self.logger)
    
    def start_http_server (self):
        thr = threading.Thread (target=self.http_server_loop)
        thr.setDaemon(True)
        thr.start()
        
    def getPendingEvents (self):
        return self.event_queue.get_pending(), self.event_queue_hi.get_pending()
    
    
    #
    # Methods to handle data set
    #
    def ingesst_data (self, path, files=None):
        ds = self.context.data_set
        if ds is None:
            ds = Data_set (path, self.logger, self.config)
            
        if not files is None:
            for f in files:
                ds.append_item(f)
    
        self.context.data_set = ds
        
