"""
Example to read a FITS file.

Created on Jul 9, 2019

Be aware that hdus.close () needs to be called to limit the number of open files at a given time.

@author: skwok
"""

import astropy.io.fits as pf
from astropy.utils.exceptions import AstropyWarning
import warnings
import numpy as np

from keckdrpframework.models.arguments import Arguments
from keckdrpframework.primitives.base_primitive import BasePrimitive


def open_nowarning(filename):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", AstropyWarning)
        return pf.open(filename, memmap=False)


class SimpleFitsReader_LRIS(BasePrimitive):
    def __init__(self, action, context):
        """
        Initializes the super class.
        """
        BasePrimitive.__init__(self, action, context)

    def _perform(self):
        """
        Expects action.args.name as fits file name
        Returns HDUs or (later) data model
        """
        name = self.action.args.name
        self.logger.debug(f"Reading {name}")
        out_args = Arguments()
        out_args.name = name
        out_args.img = self.readData(name)

        return out_args


    def readData(self, name, cutout=True):
        """
        Reads FITS file, mostly from KECK instruments.
        If there are multiple HDUs, the image is assembled according to 
        the kewyrods DETSEC and DATASEC.
        Otherwise hdus[0].data is returned.
        
        If cutout is TRUE, then only the none-zero portion is returned.
        """

        with open_nowarning(name) as hdus:
            if len(hdus) == 1:
                return hdus[0].data
            else:
                imgBuf = hdus[1].data
                for hdu in hdus[2:]:
                    imgBuf = np.concatenate((imgBuf, hdu.data), 1)
                return imgBuf

