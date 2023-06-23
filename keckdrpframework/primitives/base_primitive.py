"""
Created on Jul 8, 2019

A primitive should have:
    _pre_condition () -> bool
    _post_condition () -> bool
    _perform () -> result
    apply () -> result if success else None

    result is stored in self.result

Subclassses should be defined like this:

    def __init__(self, action, context):
         BasePrimitive.__init__(self, action, context)
        
    def _perform (self):
        ...
         do something
        ...
        
        return result
        
Recipes use apply()
        
        
@author: skwok
"""

import traceback

class BasePrimitive:
    """
    This is the base primitive.
    """

    def __init__(self, action, context):
        """
        Constructor
        """
        self.action = action
        self.context = context
        self.output = action.args
        self.logger = context.logger
        self.config = context.config

    def _pre_condition(self):
        return True

    def _post_condition(self):
        return True

    def _perform(self):
        raise Exception("Not yet implemented")

    def apply(self):
        try:
            if self._pre_condition():
                self.output = self._perform()
                if self._post_condition():
                    return self.output
        except Exception as e:
            self.logger.error(f"Failed executing primitive {self.__class__.__name__}: {e}\n{traceback.format_exc()}")
            raise(e)
        return None
    
    def __call__(self):
        """
        Makes objects of this calls callable.
        """
        return self.apply()
