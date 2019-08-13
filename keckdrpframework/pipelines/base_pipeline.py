"""
Created on Jul 8, 2019

This is the base pipeline.

@author: skwok
"""

import sys
import importlib
from keckdrpframework.utils.DRPF_logger import getLogger
from keckdrpframework.models.arguments import Arguments
from astropy.wcs.docstrings import name


class Base_pipeline:
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """
        self.event_table0 = {
            "noop":     ("noop", None, None),
            "echo":      ("echo", "stop", None),
            "time_tick": ("echo", None, None),
            }
        self.logger = getLogger()

    def true (self, *args, **kargs):
        return True
    
    def not_found (self, name):
        """
        When no action is found, this method builds a dummy function that 
        returns a dummy arguments. 
        """

        def f (action, context, **kargs):
            return Arguments(kargs=kargs, not_found=name)

        self.logger.info(f"Action not found {name}")
        return f
    
    def set_logger (self, lger):
        self.logger = lger
    
    def _get_action_apply_method (self, klass):
        """
        Returns a function that instantiates the klass and calls apply()
        """

        def f (action, context):
            obj = klass (action, context)
            return obj.apply()

        return f
            
    def _find_import_action (self, module_name):
        """
        module_name is same as class_name.
        For example: class abc is defined in primitives.abc.
        """   
        full_name = "primitives." + module_name.lower()        
        mod = importlib.import_module(full_name)        
        return self._get_action_apply_method(getattr (mod, module_name))        
    
    def _get_action (self, prefix, action):  
        """
        Returns a function for the given action name or true() if not found
        """      
        name = prefix + action
        
        try:
            fn = getattr (sys.modules[self.__module__], name)
            if isinstance (fn, type):
                return self._get_action_apply_method(fn)
            return fn
        except:
            pass
        
        try:
            # Checks if method defined in the class
            return self.__getattribute__ (name)            
        except:
            pass
    
        try:
            return self._find_import_action (name)
        except:
            pass
        
        return None        
        
    def get_pre_action (self, action):
        f = self._get_action ("pre_", action)
        if f is None:
            return self.true
        return f
    
    def get_post_action (self, action):
        f = self._get_action ("post_", action)
        if f is None:
            return self.true
        return f
    
    def get_action (self, action):
        f = self._get_action("", action)
        if f is None:
            return self.not_found(action)
        return f
    
    def noop (self, action, context):
        self.logger.info ("NOOP action")
    
    def no_more_action (self, ation, context):
        self.logger.info ("No more action, terminating")
        
    def echo (self, action, context):
        self.logger.info  (f"Echo action {action}")
        
    def _event_to_action (self, event, context):
        """
        Returns the event_info as (action, state, next_event)
        """
        noop_event = self.event_table0.get("noop")
        event_info = self.event_table0.get(event.name, noop_event)
        return event_info
    
    def event_to_action (self, event, context):
        event_info = self.event_table.get(event.name)
        if not event_info is None:
            return event_info
        return self._event_to_action(event, context)

