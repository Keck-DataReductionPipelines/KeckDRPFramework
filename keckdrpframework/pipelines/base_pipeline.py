"""
Created on Jul 8, 2019

This is the base pipeline.

The event table (or event_table0) has entries like:
    event_name: ("action_name", "new_state", "next_event")

action_name is a string. 
if action_name is a simple name, ie no packages:
    
    action_name is a method in this class or subclass
    then use that method.

    action_name is a function in this module,
    then use that function.

    action_name is a class, defined in this module,
    then use the apply() method of that class

action_name is a class, and name has packages,
then use the apply() method of that class.

@author: skwok
"""

import sys
import time
import importlib
from keckdrpframework.models.arguments import Arguments


class BasePipeline:
    """
    This is the base pipeline. 
    All pipelines should be subclassed from this class.
    """

    def __init__(self, context):
        """
        BasePipeline constructor.
        context is model.processing_context.
        """

        # Entries are:
        # name: ("action_name", "new state", "next event")
        self.event_table0 = {
            "noop": ("noop", None, None),
            "echo": ("echo", "stop", None),
            "no_event": ("no_event", None, None),
            "info": ("info", None, None),
        }

        self.context = context
        self.logger = context.logger
        self.config = context.config

    def true(self, *args, **kargs):
        return True

    def not_found(self, name):
        """
        Builds a fake action.
        When no action is found, this method builds a dummy function that 
        returns a dummy arguments. 

        Returns a function that returns an Arguments class.
        """

        def f(action, context, **kargs):
            return None

        self.logger.warn(f"Action not found {name}")
        return f

    def _get_action_apply_method(self, klass):
        """
        Helper function.
        Returns a function that instantiates the klass and calls apply()
        """

        def f(action, context):
            obj = klass(action, context)
            return obj.apply()

        return f

    def _find_import_action(self, module_name):
        """
        Helper function to find class the matches the given module name.
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
            self.context.logger.debug(f"Importing mod {mod_prefix}, name {name}")
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

        if self.config.print_trace:
            self.logger.error(f"Exception while importing {last_part} from {prefixes}")
        return None

    def _get_action(self, prefix, action):
        """
        Helper function to find the given action.
        Returns a function for the given action name or true() if not found
        """
        parts = action.split(".")
        if len(parts) == 1:
            name = prefix + action

            try:
                # Checks if method defined in the class
                return self.__getattribute__(name)
            except Exception as e2:
                if self.config.print_trace:
                    self.logger.debug(f"Name in {name} class ? {e2}")

            # Is this name defined in this module ?
            if hasattr(sys.modules[self.__module__], name):
                fn = getattr(sys.modules[self.__module__], name)

                # Name is defined, is it a class, convert it into a function
                if isinstance(fn, type):
                    return self._get_action_apply_method(fn)
                # name is a function, return it
                return fn
            else:
                if self.config.print_trace:
                    self.logger.debug(f"Not defined in module {name}")

        # Action is a class
        if len(prefix) == 0:
            # pre, post conditions are implemented inside the class
            act_method = self._find_import_action(action)
            if act_method is not None:
                return act_method

        # Could not find the name for this action
        return None

    def get_pre_action(self, action):
        """
        Returns the pre_condition.
        """
        f = self._get_action("pre_", action)
        if f is None:
            return self.true
        return f

    def get_post_action(self, action):
        """
        Returns the post_condition
        """
        f = self._get_action("post_", action)
        if f is None:
            return self.true
        return f

    def get_action(self, action):
        """
        Finds and returns the action, as a function.
        """
        f = self._get_action("", action)
        if f is None:
            return self.not_found(action)
        return f

    def noop(self, action, context):
        """
        One of the default actions.
        """
        # self.logger.info ("NOOP action")
        return action.args

    def info(self, action, context):
        """
        One of the default actions.
        Useful for testing.
        """
        pending_events = context.event_queue.get_pending()
        self.logger.info("Pending events " + str(pending_events))
        return action.args

    def echo(self, action, context):
        """
        Test action 'echo'
        """
        self.logger.info(f"Echo action {action}")
        return action.args

    def no_event(self, action, context):
        """
        The no_event event.
        """
        wait_time = min(30, max(5, self.context.config.no_event_wait_time))
        self.logger.debug(f"No event in queue, waiting {wait_time} s before continuing")
        time.sleep(wait_time)
        return action.args

    def _event_to_action(self, event, context):
        """
        Lookup function helper.
        Returns the event_info as (action, state, next_event)
        """
        event_info = self.event_table0.get(event.name)
        if event_info is None:
            self.logger.warn(f"Event {event.name} not found ")
            event_info = self.event_table0.get("noop")
        return event_info

    def event_to_action(self, event, context):
        """
        Lookup function.
        Checks the local event_table, 
        if no matching event found, then checks the default actions in table0.
        """
        try:
            event_info = self.event_table.get(event.name)
            if not event_info is None:
                return event_info
        except:
            pass
        return self._event_to_action(event, context)
