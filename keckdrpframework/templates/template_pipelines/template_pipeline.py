"""
This is a template pipeline.

"""

from pipelines.base_pipeline import Base_pipeline

class template_pipeline (Base_pipeline):
    """
    The template pipeline.
    """
    
    event_table = {
    "next_file"     : ("simple_fits_reader", "file_ready", "file_ready"),
    "file_ready"    : ("template_action", None, None)
    }

    def __init__ (self):
        """
        Constructor
        """
        Base_pipeline.__init__(self)        
    
    def template_action (self, action, context):
        print ("Template action", action)
        return None
 