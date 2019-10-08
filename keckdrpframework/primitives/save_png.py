"""
Created on Jul 8, 2019
                
@author: skwok
"""

import numpy as np
import os
import os.path

from keckdrpframework.models.arguments import Arguments
from keckdrpframework.primitives.base_primitive import Base_primitive
import matplotlib.pyplot as plt


class save_png(Base_primitive):
    """
    classdocs
    """

    def __init__(self, action, context):
        """
        Constructor
        """    
        Base_primitive.__init__(self, action, context)
        
    def _perform (self):
        output_dir = self.config.output_directory
        os.makedirs(output_dir, exist_ok=True)
        args = self.action.args
        name = os.path.basename(args.name)
        
        os.makedirs(output_dir, exist_ok=True)
        out_name = output_dir + "/" + name.replace (".fits", ".png")
        img = args.img
        h, w = img.shape
        img1 = np.stack ((img,)*3, axis=-1)
                
        plt.imsave (out_name, img1)
        
        self.logger.info("Saved {}".format(out_name))
        out_args = Arguments(name=out_name)
        return out_args
            
