'''
Created on Jul 31, 2019
                
@author: skwok
'''

import numpy as np

from keckdrpframework.primitives.base_primitive import Base_primitive
#from primitives.simple_fits_reader import open_nowarning

import astropy.io.fits as pf

class Base_img (Base_primitive):
    '''
    A collection of 2d img operations
    This class is expected to be subclassed.
    '''

    def __init__(self, action, context):
        '''
        Constructor
        '''    
        Base_primitive.__init__(self, action, context)
        
    
    def average (self, file_list):
        nfiles = len(file_list)
        if nfiles < 0:
            return None            

        hdus = open_nowarning(file_list[0])        
        stacked = np.copy (hdus[0].data)
        if nfiles == 1:
            return stacked
        
        for b in file_list[1:]:
            hdus = open_nowarning(b)
            stacked = stacked + hdus[0].data
        hdus = None
        stacked = stacked / nfiles
        return stacked


        

    def save_fits_like (self, new_name, img, like_file, new_imtype):
        hdus = open_nowarning (like_file)
        hdr = hdus[0].header
        hdr["IMTYPE"] = new_imtype
        fname = self.context.config.temp_directory + "/" + new_name
        self.logger.info (f"Saving {fname}")
        pf.writeto (fname, img, hdr, overwrite=True)
    
    def _perform (self):
        """
        Returns an Argument() with the parameters that depends on this operation.
        """
        raise Exception ("NI")
