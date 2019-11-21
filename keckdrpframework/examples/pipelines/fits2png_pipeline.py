"""
Example: FITS to PNG Pipeline


This is to demonstrate and test the framework.
For each FITS file in a given directory, a PNG file is produced.

To simulate multiple steps, a simple noise removal median filter and a histogram equalization will applied before the 
actual PNG conversion.  

Created on Jul 8, 2019

@author: skwok
"""

from keckdrpframework.pipelines.base_pipeline import BasePipeline

from keckdrpframework.primitives.create_contact_sheet_HTML import CreateContactSheetHTML


class Fits2pngPipeline(BasePipeline):
    """
    Pipeline to convert FITS to PNG including median noise removal and histogram equalization.
    
    """

    event_table = {
        "next_file": ("simple_fits_reader", "file_ready", "file_ready"),
        "file_ready": ("noise_removal", "noise_removed", "noise_removed"),
        "noise_removed": ("hist_equal2d", "histeq_done", "histeq_done"),
        "histeq_done": ("save_png", None, None),
        "contact_sheet": ("contact_sheet", None, None),
    }

    def __init__(self):
        """
        Constructor
        """
        BasePipeline.__init__(self)
        self.cnt = 0

    def set_context(self, context):
        """
        Additional initialization of context
        """
        self.context = context

    def post_save_png(self, action, context):
        self.cnt += 1
        return True

    def pre_contact_sheet(self, action, context):
        if self.cnt > 0 and self.cnt < action.args.cnt:
            context.push_event("contact_sheet", action.args)

        return True

    def contact_sheet(self, action, context):
        """
        If cnt < 0 then apply immediately.
        """
        if self.cnt < 0 or self.cnt >= action.args.cnt:
            ch = CreateContactSheetHTML(action, context)
            return ch.apply()
        return None


if __name__ == "__main__":
    """
    Standalone test
    """
    pass
