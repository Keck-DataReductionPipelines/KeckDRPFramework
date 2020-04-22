"""
Example: FITS to PNG Pipeline


This is to demonstrate and test the framework.
For each FITS file in a given directory, a PNG file is produced.

To simulate multiple steps, a simple noise removal median filter and a histogram equalization will applied before the 
actual PNG conversion.  

Created on Jul 8, 2019

@author: skwok
"""

from configparser import ConfigParser
from keckdrpframework.pipelines.base_pipeline import BasePipeline


class Fits2pngPipeline(BasePipeline):
    """
    Pipeline to convert FITS to PNG including median noise removal and histogram equalization.
    
    """

    event_table = {
        "next_file": ("simple_fits_reader.SimpleFitsReader", "file_ready", "file_ready"),
        "file_ready_for_noise_removal": ("noise_removal", "noise_removed", "noise_removed"),
        "noise_removed": ("hist_equal2d", "histeq_done", "histeq_done"),
        "file_ready": ("hist_equal2d", "histeq_done", "histeq_done"),
        "histeq_done": ("save_png", None, None),
        "contact_sheet": ("create_contact_sheet_HTML", None, None),
    }

    def __init__(self, context):
        """
        Constructor
        """
        super(Fits2pngPipeline, self).__init__(context)
        self.context = context

        fits2png = ConfigParser()
        fits2png.read("fits2png.cfg")

        self.context.config.fits2png = fits2png

        self.cnt = 0


if __name__ == "__main__":
    """
    Standalone test
    """
    pass
