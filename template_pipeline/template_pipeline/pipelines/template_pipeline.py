"""
My instrument

@author:
"""

from keckdrpframework.pipelines.base_pipeline import Base_pipeline

from ..primitives.template_primitives import *

class Template_pipeline(Base_pipeline):
    """
    Pipeline to process Keck data

    """

    event_table = {
        #"next_file": ("ingest_file", "file_ingested", None),
        "next_file": ("ingest_file", "file_ingested", "file_ingested"),
        "file_ingested": ("action_planner", None, None),
        # BIAS
        "process_bias": ("process_bias", None, None),
        # FLAT
        "process_flat": ("process_flat", None, None),
    }

    def __init__(self):
        """
        Constructor
        """
        Base_pipeline.__init__(self)
        self.cnt = 0

    def action_planner (self, action, context):
        if action.args.imtype == "BIAS":
            bias_args = Arguments(name="bias_args",
                                  groupid = groupid,
                                  want_type="BIAS",
                                  new_type="MASTER_BIAS",
                                  min_files=context.config.instrument.bias_min_nframes,
                                  new_file_name="master_bias_%s.fits" % groupid)
            context.push_event("process_bias", bias_args)
        elif "CONTBARS" in action.args.imtype:
            context.push_event("process_contbars", action.args)
        elif "FLAT" in action.args.imtype:
            context.push_event("process_flat", action.args)
        elif "ARCLAMP" in action.args.imtype:
            context.push_event("process_arc", action.args)
        elif "OBJECT" in action.args.imtype:
            context.push_event("process_object", action.args)



if __name__ == "__main__":
    """
    Standalone test
    """
    pass