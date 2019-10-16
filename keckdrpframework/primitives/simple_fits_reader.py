"""
Created on Jul 9, 2019

Be aware that hdus.close () needs to be called to limit the number of open files at a given time.
                
@author: skwok
"""

import astropy.io.fits as pf 
from astropy.utils.exceptions import AstropyWarning
import warnings

from keckdrpframework.models.arguments import Arguments
from keckdrpframework.primitives.base_primitive import Base_primitive

def open_nowarning (filename):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", AstropyWarning)
        return pf.open(filename, memmap=False)

class simple_fits_reader (Base_primitive):
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
        Expects action.args.name as fits file name
        Returns HDUs or (later) data model
        """
        name = self.action.args.name
        self.logger.info (f"Reading {name}")
        out_args = Arguments()
        out_args.name = name
        out_args.hdus = open_nowarning(name)
        
        return out_args
    
         
           
