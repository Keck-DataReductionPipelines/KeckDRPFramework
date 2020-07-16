"""
Created on Jul 8, 2019
                
@author: skwok
"""

from keckdrpframework.primitives.base_primitive import BasePrimitive


class Template(BasePrimitive):
    """
    This is a template for primitives, which is usually an action.
    
    The methods in the base class can be overloaded:
    - _pre_condition
    - _post_condition
    - _perform
    - apply
    - __call__
    """

    def __init__(self, action, context):
        """
        Constructor
        """
        BasePrimitive.__init__(self, action, context)

    def _perform(self):
        """
        Returns an Argument() with the parameters that depends on this operation.
        """
        raise Exception("Not yet implemented")
