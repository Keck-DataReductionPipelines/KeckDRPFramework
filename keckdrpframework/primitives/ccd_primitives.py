"""
Examples of subclasses of BaseImg and BasePrimitive.

A primitive can be:
  - a subclass of BasePrimitive or its subclasses
  - a function (action, context)

Created on Jul 31, 2019
                
@author: skwok
"""

from keckdrpframework.primitives.base_primitive import BasePrimitive
from keckdrpframework.primitives.base_img import BaseImg
from keckdrpframework.models.arguments import Arguments

from keckdrpframework.primitives.hist_equal2d import HistEequal2d
from keckdrpframework.primitives.simple_fits_reader import SimpleFitsReader
from keckdrpframework.primitives.save_png import SavePpng
from keckdrpframework.primitives.noise_removal import NoiseRemoval


class BaseCcdPrimitive(BaseImg):
    def __init__(self, action, context):
        BaseImg.__init__(self, action, context)

    def _pre_condition(self):
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

            self.logger.debug(f"pre condition got {nfiles}, expecting {args.min_files}")
            if nfiles < 1 or nfiles < args.min_files:
                return False
            return True
        except Exception as e:
            self.logger.error(f"Exception in base_ccd_primitive: {e}")
            return False

    def _perform(self):
        """
        Returns an Argument() with the parameters that depends on this operation.
        """
        args = self.action.args

        df = self.context.data_set.data_table
        files = df[df.IMTYPE == args.want_type]
        stacked = self.average(list(files.index))
        self.save_fits_like(args.new_file_name, stacked, files.index[0], args.new_type)
        return Arguments(name=args.new_file_name)


class ProcessBias(BaseCcdPrimitive):
    """
    Example using subclassing, where parameters are in action.args
    Builds a master bias frame and saves it to temp/stacked.fits with IMTYPE = "MASTER_BIAS"
    """

    def __init__(self, action, context):
        BaseCcdPrimitive.__init__(self, action, context)


class ProcessObject(BasePrimitive):
    """
    Example using other primitives
    """

    def __init__(self, action, context):
        BasePrimitive.__init__(self, action, context)

    def _perform(self):
        self.action.args = simple_fits_reader(self.action, self.context)()
        self.action.args = noise_removal(self.action, self.context)()
        return hist_equal2d(self.action, self.context)()


def process_flat(action, context):
    """
    Example of a function as primitive
    """
    args = simple_fits_reader(action, context)()
    img = args.hdus[0].data
    name = args.name
    minV, maxV, std = img.min(), img.max(), img.std()
    context.logger.debug(f"{name}, min={minV}, max={maxV}, std={std}")
    return Arguments(name="OK")
