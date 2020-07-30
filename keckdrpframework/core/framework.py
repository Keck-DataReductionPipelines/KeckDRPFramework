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
import sys
import os

from keckdrpframework.core import queues

# Server Task import
from keckdrpframework.core.server_task import DRPFServerHandler

from keckdrpframework.models.processing_context import ProcessingContext
from keckdrpframework.models.arguments import Arguments
from keckdrpframework.models.action import Action
from keckdrpframework.models.event import Event
from keckdrpframework.models.data_set import DataSet
from keckdrpframework.utils.drpf_logger import getLogger

from keckdrpframework.config.framework_config import ConfigClass


class Framework(object):
    """
    This class implements the core of the framework.

    The processing is event driven.
    An event can be defined as a change in set of items of interest, for example files or directories, or something in memory.
    Events are appended to a queue. Events are associated with arguments, such time, name of files, or new values of some variables.
    In a loop, an event is taken out from the queue and translated into an action.

    An action is a call to a regular function, a method in the pipeline class or in a regular class. 

    If desired, a Data_set() can created to keep a list of files in memory.

    Attributes
    ----------
    config : ConfigClass
        Instance of ConfigClass that uses the configuration file to create a set of configuration parameters

    logger : log

    pipeline : pipeline
        pipeline can be a string, a module, a class or an object of subclass base_pipeline
        The pipeline that will be used in the framework

    context :
        Instance of Processing_context, which passed along to all processing steps.

    on_state (action, context):
        A callback to change the context.state if desired, for example to force to continue or to stop

    on_exit (status)"
        Called after exiting the main_loop and before exiting. 
        Pipeline clean up code should be here.

    on_error(action, context, exception):
        Called when an exception is caught and passed to the pipeline.
        User should define their own on_error() function.
        See test_run_example.py.

    """

    def __init__(self, pipeline_name, configFile, testing=False):
        """
        pipeline_name: name of the pipeline class containing recipes

        Creates the event_queue and the action queue
        """
        if configFile is None:
            self.config = ConfigClass()
        elif isinstance(configFile, str):
            self.config = ConfigClass(configFile)
        else:
            self.config = configFile

        self.testing = testing

        self.logger = getLogger(self.config.logger_config_file, name="DRPF")
        self.logger.info("")
        self.logger.info("Initialization Framework cwd={}".format(os.getcwd()))

        self.wait_for_event = False
        # The high priority event queue is local to the process
        self.event_queue_hi = queues.SimpleEventQueue()

        # The regular event queue can be local or shared via queue manager
        self.queue_manager = None
        self.event_queue = self._get_event_queue()

        # The done_queue
        self.done_queue = None

        # The handlers
        self.on_exit = self.default_on_exit
        self.on_state = self.default_on_state
        self.on_error = self.default_on_error

        self.context = ProcessingContext(self.event_queue, self.event_queue_hi, self.logger, self.config)

        pipeline = find_pipeline(pipeline_name, self.config.pipeline_path, self.context, self.logger)

        if pipeline is None:
            raise Exception(f"Failed to initialize pipeline {pipeline_name}")

        self.pipeline = pipeline

        self.keep_going = True
        self.init_signal()
        self.store_arguments = Arguments()

    def _get_queue_manager(self, cfg):
        """
        Tries to get an event queue. 
        If successful then returns the manager and the queue, 
        otherwise starts the new queue manager. 
        """
        hostname = cfg.queue_manager_hostname
        portnr = cfg.queue_manager_portnr
        auth_code = cfg.queue_manager_auth_code

        self.logger.debug(f"Getting shared event queue from {hostname}:{portnr}")
        queue = queues.get_event_queue(hostname, portnr, auth_code)
        if queue is None:
            self.logger.debug("Starting Queue Manager")
            self.queue_manager = queues.start_queue_manager(hostname, portnr, auth_code, self.logger)
            queue = queues.get_event_queue(hostname, portnr, auth_code)
            if queue is not None:
                self.logger.debug("Got event queue from Queue Manager")
            return queue
        else:
            return queue

    def _get_event_queue(self):
        """
        If multiprocessing is desired then returns the shared queue,
        otherwise returns the Simple_event_queue, which will only work within a single process.
        """
        cfg = self.config
        want_multi = cfg.getValue("want_multiprocessing", False)

        if want_multi:
            return self._get_queue_manager(cfg)

        return queues.SimpleEventQueue()

    def get_event(self):
        """
        Retrieves and returns an event from the queues.
        First it checks the high priority queue, if fails then checks the regular event queue.

        If there are no more events, then it returns the no_event_event, which is defined in the configuration.
        """
        try:
            try:
                return self.event_queue_hi.get(block=False)
            except:
                ev = self.event_queue.get(block=True, timeout=self.config.event_timeout)
                self.wait_for_event = False
                return ev
        except Exception as e:
            if self.wait_for_event:
                ev = Event("no_event", None)
            else:
                ev = self.config.no_event_event
            if ev is None:
                return None
            ev.args = Arguments(name=ev.name, time=datetime.datetime.ctime(datetime.datetime.now()))
            return ev

    def _push_event(self, event_name, args):
        """
        Pushes high priority events

        Normal events go to the lower priority queue
        This method is only used in execute.

        """
        self.logger.debug(f"Push event {event_name}, {args.name}")
        self.event_queue_hi.put(Event(event_name, args))

    def append_event(self, event_name, args, recurrent=False):
        """
        Appends low priority event to the end of the queue
        """
        if args is None:
            args = self.store_arguments
        self.event_queue.put(Event(event_name, args, recurrent))

    def event_to_action(self, event, context):
        """
        Returns an Action()
        Passes event.args to action.args.        
        Note that event.args comes from previous action.output.

        This method is called in the action loop.
        The actual event_to_action method is defined in the pipeline and it depends on the incoming event and context.state.

        """
        event_info = self.pipeline.event_to_action(event, context)
        self.logger.debug(f"Event to action {event_info}")
        return Action(event, event_info, args=event.args)

    def execute(self, action, context):
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
                    self.logger.debug("Executing action " + action.name)

                # Run action
                action_output = pipeline.get_action(action_name)(action, context)
                action.output = action_output
                if action_output is not None:
                    self.store_arguments = action_output
                else:
                    self.store_arguments = action.args

                # Post condition
                if pipeline.get_post_action(action_name)(action, context):
                    if not action.new_event is None:
                        # Post new event
                        new_args = self.store_arguments if action_output is None else action_output
                        self._push_event(action.new_event, new_args)

                    if not action.next_state is None:
                        # New state
                        context.state = action.next_state

                    if self.config.print_trace:
                        self.logger.debug("Action " + action.name + " done")
                    return
                else:
                    # Post-condition failed
                    context.state = "stop"
            else:
                # Failed pre-condition
                if self.config.pre_condition_failed_stop:
                    context.state = "stop"
                else:
                    self.store_arguments = action.args
        except Exception as e:
            if self.testing:
                raise  # reraise so that testing infrastructure catches it
            else:
                self.logger.error(f"Exception {e} while invoking {action_name}")
                context.state = "stop"
                self.on_error(action, context, e)
                if self.config.print_trace:
                    traceback.print_exc()

    def _action_completed(self, successful, action):
        event = action.event
        id = event.id
        try:
            argname = event.args.name
        except:
            argname = "Undef"
        if successful:
            self.logger.info(
                f"Event completed: name {event.name}, action {action.name}, arg name {argname}, recurr {event._recurrent}"
            )
        else:
            self.logger.info(
                f"Event failed: name {event.name}, action {action.name}, arg name {argname}, recurr {event._recurrent}"
            )
        try:
            if self.event_queue.get_in_progress().get(id):
                self.event_queue.discard(id)
                if event._recurrent:
                    self.append_event(event.name, event.args, event._recurrent)
            elif self.event_queue_hi.get_in_progress().get(id):
                self.event_queue_hi.discard(id)
        except Exception as e:
            self.logger.error(f"Exception occured while in _action_completed, {e}")

    def main_loop(self):
        """
        This is the main action loop.

        This method can be called directly to run in the main thread.
        To run in a thread, use start_action_loop(). 
        """
        success = False
        self.keep_going = True
        while self.keep_going:
            try:
                action = ""
                success = False
                event = self.get_event()
                if event is None:
                    self.logger.info("No new events - do nothing")

                    if self.event_queue.qsize() == 0 and self.event_queue_hi.qsize() == 0:
                        self.logger.debug(f"No pending events or actions, terminating")
                        self.keep_going = False
                        if self.queue_manager is not None:
                            try:
                                self.event_queue.terminate()
                            except:
                                pass
                    continue

                action = self.event_to_action(event, self.context)
                self.execute(action, self.context)
                success = action.output is not None
                self.on_state(action, self.context)
                if self.context.state == "stop":
                    break
            except BrokenPipeError as bpe:
                self.logger.error(f"Failed to get retrieve events. Queue may be closed.")
                break
            except Exception as e:
                if self.testing:
                    self.logger.info("Reraising exception (testing mode)")
                    raise  # exceptions caught by testing framework, not here
                else:
                    self.logger.error(f"Framework main_loop: Exception while processing action {action}, {e}")
                    self.on_error(action, self.context, e)
                    if self.config.print_trace:
                        traceback.print_exc()

            self._action_completed(success, action)

        self.keep_going = False
        self.logger.info("Exiting main loop")

    def _main_loop_helper(self):
        self.main_loop()
        self.on_exit(0)

    def start_action_loop(self):
        """
        This is a thread running the action loop.
        """
        thr = threading.Thread(name="action_loop", target=self._main_loop_helper)
        thr.setDaemon(True)
        thr.start()

    def init_signal(self):
        """
        Captures keyboard interrupt
        """

        def handler(signum, *args):
            self.logger.error(f"Signal {signum} received")
            self.keep_going = False

        try:
            signal.signal(signal.CTRL_BREAK_EVENT, handler)
        except:
            pass
        signal.signal(signal.SIGINT, handler)

    def _start(self):
        """
        Starts the event loop and the action loop
        """
        self.start_action_loop()

    def end(self):
        """
        Releases the event_queue.
        Needed when a client ingest_data and then quits.
        """
        try:
            self.event_queue.close()
        except:
            pass

    def wait_for_ever(self):
        """
        Because the action loops runs in a thread, this methods waits until keep_going is false.         
        """
        while self.keep_going:
            time.sleep(1)

    def get_pending_events(self):
        return self.event_queue.get_pending(), self.event_queue_hi.get_pending()

    #
    # Methods to handle data set
    #
    def ingest_data(self, path=None, files=None, monitor=False):
        """
        Adds files to the data_set.
        The data_set resides in the framework context.
        """
        ds = self.context.data_set
        if ds is None:
            # Data_set will scan and import the content of the directory
            ds = DataSet(path, self.logger, self.config, self.context.event_queue)

        if files is not None:
            if type(files) == str:
                self.logger.info(f"ingest {files}")
                ds.append_item(files)
            else:
                for f in files:
                    ds.append_item(f)

        # for ditem in ds.data_table.index:
        #    self.logger.info("File ingestion: pushing next file event to the queue")
        #    self.event_queue.put(Event("next_file", Arguments(name=ditem)))

        self.context.data_set = ds
        if monitor:
            self.context.data_set.start_monitor()

    def start(self, qm_only=False, ingest_data_only=False, wait_for_event=False, continuous=False):
        if qm_only:
            self.logger.info("Queue manager only mode, no processing")
            self.wait_for_ever()
        else:
            if ingest_data_only:
                # Release the queue
                self.end()
            else:
                if continuous:
                    self.config.no_event_event = Event("no_event", None)
                self.wait_for_event = wait_for_event
                self._start()
                self.logger.info("Framework main loop started")
                self.wait_for_ever()

    def default_on_exit(self, status=0):
        """
        Hook, called before exiting
        Subclasses can override to continue in the main_loop or call exit(status)
        Let applications register callback or subclassing
        """
        os._exit(status)

    def default_on_state(self, action, context):
        """
        Hook to change context state.
        Default is to ignore state = 'stop'.
        To terminate, override this method to return 'stop'.
        """
        if context.state == "stop":
            context.state = "ready"

    def default_on_error(self, action, context, exception):
        """
        Hook for error handling
        Default is do nothing
        Alternative is raise exception
        """
        return


def find_pipeline(pipeline_name, pipeline_path, context, logger):
    def to_camel_case(instr):
        out = []
        flag = True
        for c in instr:
            if flag:
                out.append(c.upper())
                flag = False
                continue
            if c == "_":
                flag = True
                continue
            out.append(c)
        return "".join(out)

    """
    Finds the class called pipeline_name and instantiates an object of that class.
    """

    if not isinstance(pipeline_name, str):  # not string
        if isinstance(pipeline_name, type):  # is a class, ie. a.b
            return pipeline_name(context)
        elif isinstance(pipeline_name, type(sys)):  # is a module, ie. a.a_b_c
            last_name = pipeline_name.__name__.split(".")[-1]
            klass = getattr(pipeline_name, to_camel_case(last_name))  # try a.a_b_c.ABC
            if klass is not None:
                return klass(context)
        elif isinstance(pipeline_name, object):  # object, already an instance of a class
            return pipeline_name
        logger.error(f"{pipeline_name} must be a module, a class, an object or a string")
        return None

    #
    # pileline_name is a tring
    #
    parts = pipeline_name.split(".")
    module_name = ".".join(parts[:-1])
    last_name = parts[-1]

    klass = None
    try:
        if len(parts) > 1:
            # Converts a.a_b_c.a_b_c to a.a_b_c.ABC
            # and instantiates an object of the class ABC
            module = importlib.import_module(module_name)
            klass = getattr(module, to_camel_case(last_name))
            if klass is not None:
                return klass(context)
    except Exception as me:
        logger.debug(f"Failed loading as string {pipeline_name}")
        logger.debug(f"Trying {pipeline_path} next")

    if pipeline_path is None:
        pipeline_path = ("",)
    for p in pipeline_path:
        try:
            full_name = pipeline_name
            if p:
                full_name = f"{p}.{pipeline_name}"
            module = importlib.import_module(full_name)
            class_name = to_camel_case(last_name)
            if hasattr(module, class_name):
                klass = getattr(module, class_name)
                if klass is not None:
                    logger.debug(f"Found {class_name} in {full_name}")
                    break
            logger.debug(f"Class {class_name} not in {full_name}")
        except ModuleNotFoundError as me:
            logger.debug(f"Failed loading pipeline {full_name}, {me}")
            continue
        except Exception as e:
            logger.error(f"Exception {e}")
            break

    if klass is not None:
        return klass(context)

    logger.error(f"Could not find pipeline {pipeline_name} in {pipeline_path}")

    return None


def create_context(event_queue=None, event_queue_hi=None, logger=None, config=None):
    """
    Convenient function to create a context for working withtout the framework.
    Useful in Jupyter notebooks for example.

    """
    if config is None:
        config = ConfigClass()

    if logger is None:
        logger = getLogger(config.logger_config_file, name="DRPF")

    if event_queue_hi is None:
        event_queue_hi = queues.SimpleEventQueue()

    if event_queue is None:
        event_queue = queues.SimpleEventQueue()

    return ProcessingContext(event_queue, event_queue_hi, logger, config)
