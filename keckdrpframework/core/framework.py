"""
Basic framework module

This is the main module implementing the framework.

@author:  skwok
"""

import datetime
import threading
import signal
import traceback
import time
import importlib
import os

from keckdrpframework.core import queues

# Server Task import
from keckdrpframework.core.server_task import DRPF_server_handler, start_http_server

from keckdrpframework.models.processing_context import Processing_context
from keckdrpframework.models.arguments import Arguments
from keckdrpframework.models.action import Action
from keckdrpframework.models.event import Event
from keckdrpframework.models.data_set import Data_set
from keckdrpframework.pipelines.base_pipeline import Base_pipeline
from keckdrpframework.utils.DRPF_logger import getLogger
from keckdrpframework.config.framework_config import ConfigClass


class Framework(object):
    """
    This class implements the core of the framework.
    
    The processing is event driven.
    An event can be defined as a change in set of items of interest, for example files or directories, or something in memory.
    Events are appended to a queue. Events are associated with arguments, such time, name of files, or new values of some variables.
    In a loop, an event is taken out from the queue and translated into an action.
    
    An action is a call to a regular function, a method in the pipeline class or in a regular class. 
    
    If desired, an simple HTTP server can be started via start_http_server().
    
    If desired, a Data_set() can created to keep a list of files in memory.
    
    Attributes
    ----------
    config : ConfigClass
        Instance of ConfigClass that uses the configuration file to create a set of configuration parameters
    
    logger : log
    
    pipeline : pipeline
        The pipeline that will be used in the framework
        
    context :
        Instance of Processing_context, which passed along to all processing steps.
    """
    
    def __init__(self, pipeline_name, configFile):
        """
        pipeline_name: name of the pipeline class containing recipes
        
        Creates the event_queue and the action queue
        """

        if isinstance(configFile, str):
            self.config = ConfigClass(configFile)
        else:
            self.config = configFile

        self.logger = getLogger (self.config.logger_config_file, name="DRPF")
        
        self.wait_for_event = False
        # The high priority event queue is local to the process
        self.event_queue_hi = queues.Simple_event_queue()
        
        # The regular event queue can be local or shared via proxy manager
        self.queue_manager = None
        self.event_queue = self._get_event_queue ()

        if isinstance(pipeline_name, str):
            pipeline = find_pipeline (pipeline_name, self.config.pipeline_path, self.logger)
        else:
            pipeline = pipeline_name()
        if pipeline is None:
            raise Exception ("Failed to initialize pipeline")
          
        self.context = Processing_context (self.event_queue, self.event_queue_hi, self.logger, self.config)
        pipeline.set_logger (self.logger)
        pipeline.set_context (self.context)
        self.pipeline = pipeline
                
        self.keep_going = True
        self.init_signal ()
        self.store_arguments = Arguments()
        
    
    def start_queue_manager (self):    
        cfg = self.config
        
        hostname = cfg.queue_manager_hostname
        portnr = cfg.queue_manager_portnr
        auth_code = cfg.queue_manager_auth_code                      
        queues._queue_manager_target (hostname, portnr, auth_code)
            

    def _get_event_queue (self):
        """
        If multiprocessing is desired then returns the shared queue,
        otherwise returns the Simple_event_queue, which will only work within a single process.
        """
        cfg = self.config
        want_multi = cfg.get("want_multiprocessing", False)
        
        if want_multi:            
            hostname = cfg.queue_manager_hostname
            portnr = cfg.queue_manager_portnr
            auth_code = cfg.queue_manager_auth_code    
            self.logger.info("Getting shared event queue")         
            return queues.get_event_queue (hostname, portnr, auth_code)
            
        return queues.Simple_event_queue()        
    
    def get_event (self):
        """
        Retrieves and returns an event from the queues.
        First it checks the high priority queue, if fails then checks the regular event queue.
        
        If there are no more events, then it returns the no_event_event, which is defined in the configuration.
        """
        try:
            try:
                return self.event_queue_hi.get_nowait()
            except:
                ev = self.event_queue.get(True, self.config.event_timeout)
                self.wait_for_event = False
                return ev
        except Exception as e:
            if self.wait_for_event:
                ev = Event ("no_event", None)
            else:
                ev = self.config.no_event_event
            if ev is None:                    
                return None
            time.sleep(self.config.no_event_wait_time)
            ev.args = Arguments(name=ev.name, time=datetime.datetime.ctime(datetime.datetime.now()))
            return ev

    def _push_event (self, event_name, args):
        """
        Pushes high priority events
        
        Normal events go to the lower priority queue
        This method is only used in execute.
        
        """
        self.logger.info (f"Push event {event_name}, {args.name}")
        self.event_queue_hi.put(Event (event_name, args))
        
    def append_event (self, event_name, args):
        """
        Appends low priority event to the end of the queue
        """
        if args is None:
            args = self.store_arguments
        self.event_queue.put (Event (event_name, args))
                                   
    def event_to_action (self, event, context):
        """
        Returns an Action()
        Passes event.args to action.args.        
        Note that event.args comes from previous action.output.
        
        This method is called in the action loop.
        The actual event_to_action method is defined in the pipeline and it depends on the incoming event and context.state.
        
        """
        event_info = self.pipeline.event_to_action (event, context)
        self.logger.info (f"Event to action {event_info}")
        return Action (event_info, args=event.args)
    
    def execute (self, action, context):
        """
        Executes one action
        The input for the action is in action.args.
        The action returns action_output and it is passed to the next event if action is successful.
        """
        pipeline = self.pipeline
        action_name = action.name
        try:
            # Pre condition
            if pipeline.get_pre_action(action_name)(action, context):
                if self.config.print_trace:
                    self.logger.info ("Executing action " + action.name)
                
                # Run action
                action_output = pipeline.get_action(action_name)(action, context)
                if action_output is not None:
                    self.store_arguments = action_output
                    
                # Post condition
                if pipeline.get_post_action(action_name)(action, context):
                    if not action.new_event is None:
                        # Post new event
                        new_args = Arguments() if action_output is None else action_output
                        self._push_event (action.new_event, new_args)
                        
                    if not action.next_state is None:
                        # New state
                        context.state = action.next_state
                        
                    if self.config.print_trace:
                        self.logger.info ("Action " + action.name + " done")
                    return
                else:
                    # Post-condition failed
                    context.state = "stop"
            else:
                # Failed pre-condition
                if self.config.pre_condition_failed_stop:
                    context.state = "stop"
        except:
            self.logger.error ("Exception while invoking {}. Execution stopped.".format (action_name))
            context.state = "stop"
            if self.config.print_trace:
                traceback.print_exc()
    
    def main_loop (self):
        """
        This is the main action loop.
    
        This method can be called directly to run in the main thread.
        To run in a thread, use start_action_loop(). 
        """
        while self.keep_going:
            try:    
                action = ""
                event = self.get_event ()
                if event is None:
                    self.logger.info ("No new events - do nothing")
                
                    if self.event_queue.qsize() == 0 and \
                        self.event_queue_hi.qsize() == 0:
                        self.logger.info (f"No pending events or actions, terminating")
                        self.keep_going = False
                    continue                      
                     
                action = self.event_to_action (event, self.context)                        
                self.execute(action, self.context)
                if self.context.state == "stop":
                    break
            except Exception as e:
                self.logger.error (f"Exception while processing action {action}, {e}")
                if self.config.print_trace:
                    traceback.print_exc()
                break                
        self.keep_going = False
        
    def start_action_loop (self):
        """
        This is a thread running the action loop.
        """
        thr = threading.Thread (name="action_loop", target=self.main_loop)
        thr.setDaemon(True)
        thr.start()

    def init_signal (self):
        """
        Captures keyboard interrupt
        """

        def handler (signum, *args):
            self.logger.error (f"Signal {signum} received")
            self.keep_going = False

        try:
             signal.signal (signal.CTRL_BREAK_EVENT, handler)
        except:
            pass
        signal.signal (signal.SIGINT, handler)
        
    def _start (self):
        """
        Starts the event loop and the action loop
        """  
        self.start_action_loop ()
        if self.config.want_http_server:
            self.start_http_server()
        
    def end (self):
        try:        
            self.event_queue.close()
        except:
            pass
        
    def waitForEver (self):
        """
        Because the action loops runs in a thread, this methods waits until keep_going is false.         
        """
        while self.keep_going:
            time.sleep (1)
    
    #
    # Methods for HTTP server
    #
    def start_http_server (self):

        def loop ():
            start_http_server(self, self.config, self.logger)    

        thr = threading.Thread (target=loop)
        thr.setDaemon(True)
        thr.start()
        
    def getPendingEvents (self):
        return self.event_queue.get_pending(), self.event_queue_hi.get_pending()         
    
    #
    # Methods to handle data set
    #
    def ingest_data (self, path=None, files=None):
        """
        Adds files to the data_set.
        The data_set resides in the framework context.
        """
        ds = self.context.data_set
        if ds is None:
            # Data_set will scan and import the content of the directory
            ds = Data_set (path, self.logger, self.config)
            
        if files is not None:
            for f in files:
                ds.append_item(f)
        
        for ditem in ds.data_table.index:
            self.event_queue.put(Event ("next_file", Arguments(name=ditem)))
            
        self.context.data_set = ds
        
    def start (self, qm_only=False, ingest_data_only=False, wait_for_event=False, continuous=False):
        if qm_only:
            self.logger.info ("Queue manager only mode, no processing")
            self.waitForEver()
        else:          
            if ingest_data_only:
                # Release the queue
                self.end ()                
            else:
                if continuous:
                    self.config.no_event_event = Event ("no_event", None)
                self.wait_for_event = wait_for_event
                self._start()
                self.logger.info("Framework main loop started")
                self.waitForEver()

def find_pipeline (pipeline_name, prefixes, logger):
    """
    Finds the class called pipeline_name and instantiates an object of that class.
    """    
    klass = None
    for p in prefixes:
        try: 
            full_name = pipeline_name
            if p:   
                full_name = f"{p}.{pipeline_name}"
            module = importlib.import_module(full_name)
            klass = getattr (module, pipeline_name)
            if klass is not None:
                break
        except ModuleNotFoundError as me:
            print ("Failed loading pipeline", full_name, me)
            continue
        except Exception as e:            
            logger.info("Exception " + e)
            break
    
    if klass is not None:
        return klass ()
            
    logger.error(f"Could not find pipeline {pipeline_name} in {prefixes}")
           
    return None

def create_context (event_queue=None, event_queue_hi=None, logger=None, config=None):
    """
    Convenient function to create a context for working withtout the framework.
    Useful in Jupyter notebooks for example.
    
    """
    if config is None:
        config = ConfigClass ()
        
    if logger is None:
        logger = getLogger (config.logger_config_file, name="DRPF")
                   
    if event_queue_hi is None:
        event_queue_hi = queues.Simple_event_queue()
        
    if event_queue is None:        
        event_queue = queues.Simple_event_queue()        

    return Processing_context (event_queue, event_queue_hi, logger, config)
    
