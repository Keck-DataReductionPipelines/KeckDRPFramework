"""
This is a template pipeline.

"""

from keckdrpframework.pipelines.base_pipeline import BasePipeline
from keckdrpframework.models.processing_context import ProcessingContext
from keckdrpframework.primitives.simple_fits_reader import SimpleFitsReader

# MODIFY THIS IMPORT to reflect the name of the module created in the primitives directory
from template.primitives.Template import MyTemplate


class TemplatePipeline(BasePipeline):
    """
    The template pipeline.
    """

    # modify the event table to use the events actually defined in the primitives
    event_table = {

        # this is a standard primitive defined in the framework
        "next_file": ("SimpleFitsReader", "file_ready", "template"),

        # this is a primitive defined in the Template.py primitive files
        # it is imported explicitly at the top of this file because the name of the class (MyTemplate)
        # does not correspond to the name of the file (Template.py)
        "template": ("MyTemplate", "running_MyTemplate", "template2"),

        # this is a primitive defined in Template2.py
        # it does NOT need to be imported because the name of the class (Template2)
        # is the same as the name of the file (Template2.py) that defines it
        "template2": ("Template2", "running_Template2", "template_action"),

        # this is primitive defined in this file, below
        # it is used for short, generic primitives
        "template_action": ("template_action", None, None)
    }

    def __init__(self, context: ProcessingContext):
        """
        Constructor
        """
        BasePipeline.__init__(self, context)
    
    def template_action(self, action, context):
        self.logger.info("Running template_action on %s", action.args.name)
        return action.args
 