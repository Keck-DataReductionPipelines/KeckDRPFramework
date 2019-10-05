"""
Created on Jul 8, 2019
                
@author: skwok
"""

from keckdrpframework.primitives.base_primitive import Base_primitive

class Template(Base_primitive):
    """
    classdocs
    """

    def __init__(self, action, context):
        """
        Constructor
        """    
        Base_primitive.__init__(self, action, context)
        
        
    def _perform (self):
        """
        Returns an Argument() with the parameters that depends on this operation.
        """
        raise Exception ("Not yet implemented")
    
            
            