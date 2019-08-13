"""
Created on Jul 31, 2019
                
@author: skwok
"""

from primitives.base_primitive import Base_primitive
from primitives.base_img import Base_img
from models.arguments import Arguments

from primitives.hist_equal2d import hist_equal2d
from primitives.simple_fits_reader import simple_fits_reader
from primitives.save_png import save_png
from primitives.noise_removal import noise_removal

class base_ccd_primitive (Base_img):

    def __init__(self, action, context):
        Base_img.__init__(self, action, context)
    
    def _pre_condition (self):
        """
        Checks is we can build a stacked  frame
        Expected arguments:
            want_type: ie. BIAS
            min_files: ie 10
            new_type: ie MASTER_BIAS
            new_file_name: master_bias.fits
            
        """
        try:
            args = self.action.args
            df = self.context.data_set.data_table
            files = df[df.IMTYPE == args.want_type]
            nfiles = len(files)
            
            self.logger.info (f"pre condition got {nfiles}, expecting {args.min_files}")
            if nfiles < 1 or nfiles < args.min_files:
                return False
            return True
        except Exception as e:
            self.logger.error (f"Exception in base_ccd_primitive: {e}")
            return False
        
    def _perform (self):
        """
        Returns an Argument() with the parameters that depends on this operation.
        """
        args = self.action.args
        
        df = self.context.data_set.data_table
        files = df[df.IMTYPE == args.want_type]
        stacked = self.average(list(files.index))
        self.save_fits_like (args.new_file_name, stacked, files.index[0], args.new_type)
        return Arguments(name=args.new_file_name)
    
    
class process_bias (base_ccd_primitive):
    """
    Example using subclassing, where parameters are in action.args
    Builds a master bias frame and saves it to temp/stacked.fits with IMTYPE = "MASTER_BIAS"
    """
    def __init__ (self, action, context):
        base_ccd_primitive.__init__(self, action, context)
        
    
class process_object (Base_primitive):
    """
    Example using other primitives
    """
    def __init__(self, action, context):
        Base_primitive.__init__(self, action, context)
        
    def _perform (self):
        self.action.args = simple_fits_reader (self.action, self.context)()
        self.action.args = noise_removal (self.action, self.context)()
        return hist_equal2d (self.action, self.context)()
        
def process_flat (action, context):
    args = simple_fits_reader (action, context)()
    img = args.hdus[0].data
    name = args.name
    minV, maxV, std = img.min(), img.max(), img.std() 
    context.logger.info (f"{name}, min={minV}, max={maxV}, std={std}")
    return Arguments(name="OK")
    
        
    
                    
            
