'''
Created on Jul 8, 2019

A primitive should have:
    _pre_condition () -> bool
    _post_condition () -> bool
    _perform () -> result
    apply () -> result if success else None

    result is stored in self.result

Subclassses should be defined like this:

    def __init__(self, action, context):
         Base_primitive.__init__(self, action, context)
        
    def _perform (self):
        ...
         do something
        ...
        
        return result
        
Recipes use apply()
        
        
@author: skwok
'''

class Base_primitive:
    """
    This is the base primitive.
    """

    def __init__(self, action, context):
        '''
        Constructor
        '''
        self.action = action
        self.context = context
        self.output = None
        self.logger = context.logger
        self.config = context.config
        
    def _pre_condition (self):
        return True
    
    def _post_condition (self):
        return True 
    
    def _perform (self):
        raise Exception ("Not yet implemented")
    
    def apply (self):
        if self._pre_condition():
            output = self._perform()
            if self._post_condition():
                self.output = output
        return self.output
            
    def __call__ (self):
        """
        Makes objects of this calls callable.
        """
        return self.apply()
            
        