"""
This is a template pipeline.

"""

from keckdrpframework.pipelines.base_pipeline import BasePipeline

# MODIFY THIS IMPORT to reflect the name of the module created in the primitives directory
from ..primitives.template_primitive import *


class template_pipeline (BasePipeline):
    """
    The template pipeline.
    """

    # modify the event table to use the events actually defined in the primitives
    event_table = {
    # this is a standard primitive defined in the framework
    "next_file"     : ("simple_fits_reader", "file_ready", "template_primitive"),
    # this is a primitive defined in the template primitive files
    "template_primitive"    : ("Template", "running_template_primitive", "template_action"),
    # this is primitive defined in this file, below
    "template_action" : ("template_action", None, None)
    }

    def __init__ (self):
        """
        Constructor
        """
        BasePipeline.__init__(self)
    
    def template_action (self, action, context):
        print("Template action", action)
        return None
 