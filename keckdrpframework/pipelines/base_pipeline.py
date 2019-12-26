"""
Created on Jul 8, 2019

This is the base pipeline.

@author: skwok
"""

import sys
import re
import importlib
from keckdrpframework.utils.drpf_logger import getLogger
from keckdrpframework.models.arguments import Arguments


class BasePipeline:
    """
    classdocs
    """

    def __init__(self, context):
        """
        Constructor
        """
        self.event_table0 = {
            "noop": ("noop", None, None),
            "echo": ("echo", "stop", None),
            "no_event": ("no_event", None, None),
            "info": ("info", None, None),
        }
        
        self.context = context
        self.logger = context.logger

    def true(self, *args, **kargs):
        return True
    
    def not_found(self, name):
        """
        When no action is found, this method builds a dummy function that 
        returns a dummy arguments. 
        """

        def f(action, context, **kargs):
            return Arguments(kargs=kargs, not_found=name)

        self.logger.warn(f"Action not found {name}")
        return f

    def _get_action_apply_method(self, klass):
        """
        Returns a function that instantiates the klass and calls apply()
        """

        def f(action, context):
            obj = klass(action, context)
            return obj.apply()

        return f

    def _find_import_action(self, module_name):
        """
        module_name is same as file name.
        For example: class abc is defined in primitives.abc.
        """

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
        
        def get_apply_method(mod_prefix, name):
            if self.context.debug:
                self.context.logger.info(f"Importing mod {mod_prefix}, name {name}")
            try:
                mod = importlib.import_module(mod_prefix)
                if hasattr(mod, name):
                    return self._get_action_apply_method(getattr(mod, name))
            except:
                pass
            return None

        prefixes = self.context.config.primitive_path
        last_part = ""

        for p in prefixes:
            if p:
                full_name = f"{p}.{module_name}"
            else:
                full_name = module_name

            parts = full_name.split(".")
            last_part = parts[-1]
            package_name = ".".join(parts[:-1])
            
            method = get_apply_method(full_name, to_camel_case(last_part))
            if method is not None:
                return method            
            
            method = get_apply_method(package_name, last_part)
            if method is not None:
                return method
            
        self.logger.error(f"Exception while importing {last_part} from {prefixes}")
        return None

    def _get_action(self, prefix, action):
        """
        Returns a function for the given action name or true() if not found
        """
        parts = action.split(".")
        if len(parts) == 1:
            name = prefix + action

            try:
                # Checks if method defined in the class
                return self.__getattribute__(name)
            except Exception as e2:
                if self.context.debug:
                    self.logger.warn(f"Name in {name} class ? {e2}")
            
            # Is this name defined in this module ?
            if hasattr(sys.modules[self.__module__], name):
                fn = getattr(sys.modules[self.__module__], name)

                # Name is defined, is it a class, convert it into a function
                if isinstance(fn, type):
                    return self._get_action_apply_method(fn)
                # name is a function, return it
                return fn
            else:
                if self.context.debug:
                    self.logger.warn(f"Not defined in module {name}")
            
        # Action is a class
        if len(prefix) == 0:
            # pre, post conditions are implemented inside the class
            act_method = self._find_import_action(action)
            if act_method is not None:
                return act_method
                
        # Could not find the name for this action
        return None

    def get_pre_action(self, action):
        f = self._get_action("pre_", action)
        if f is None:
            return self.true
        return f

    def get_post_action(self, action):
        f = self._get_action("post_", action)
        if f is None:
            return self.true
        return f

    def get_action(self, action):
        f = self._get_action("", action)
        if f is None:
            return self.not_found(action)
        return f

    def noop(self, action, context):
        # self.logger.info ("NOOP action")
        return action.args

    def info(self, action, context):
        pending_events = context.event_queue.get_pending()
        self.logger.info("Pending events " + str(pending_events))

    def no_more_action(self, action, context):
        self.logger.info("No more action, terminating")

    def echo(self, action, context):
        """
        Test action 'echo'
        """
        self.logger.info(f"Echo action {action}")

    def no_event(self, action, context):
        """
        The no_event event.
        """
        self.logger.info("No event in queue")

    def _event_to_action(self, event, context):
        """
        Returns the event_info as (action, state, next_event)
        """
        event_info = self.event_table0.get(event.name)
        if event_info is None:
            self.logger.warn(f"Event {event.name} not found ")
            event_info = self.event_table0.get("noop")
        return event_info

    def event_to_action(self, event, context):
        """
        Checks the local event_table, 
        if no matching event found, then checks the table0.
        """
        event_info = self.event_table.get(event.name)
        if not event_info is None:
            return event_info
        return self._event_to_action(event, context)
