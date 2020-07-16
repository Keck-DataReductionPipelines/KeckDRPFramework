"""
Created on Jul 31, 2019
                
@author: skwok
"""

import numpy as np
import astropy.io.fits as pf
from keckdrpframework.primitives.base_primitive import BasePrimitive


class BaseImg(BasePrimitive):
    """
    A collection of 2d image operations.
    
    This is provided an example for subclassing BasePrimitive and implementing the desired operation.
    The actual operations implemented here are : average and save_fits_like.
    
    Applications can subclass this class and add more operations.
    
    """

    def __init__(self, action, context):
        """
        Constructor for BaseImg. 
        Invokes the super class's initialization.
        """
        BasePrimitive.__init__(self, action, context)

    def average(self, file_list):
        """
        Given a list of fits files, assuming  all have the same dimension,
        Returns the average as np.array()
        """
        nfiles = len(file_list)
        if nfiles < 0:
            return None

        hdus = open_nowarning(file_list[0])
        stacked = np.copy(hdus[0].data)
        if nfiles == 1:
            return stacked

        for b in file_list[1:]:
            hdus = open_nowarning(b)
            stacked = stacked + hdus[0].data
        hdus = None
        stacked = stacked / nfiles
        return stacked

    def save_fits_like(self, new_name, img, like_file, new_imtype):
        """
        Saves img to a file as fits file using headers from like_file
        """
        hdus = open_nowarning(like_file)
        hdr = hdus[0].header
        hdr["IMTYPE"] = new_imtype
        fname = self.context.config.temp_directory + "/" + new_name
        self.logger.debug(f"Saving {fname}")
        pf.writeto(fname, img, hdr, overwrite=True)

    def _perform(self):
        """
        Returns an Argument() with the parameters that depends on this operation.
        """
        raise Exception("NI")
