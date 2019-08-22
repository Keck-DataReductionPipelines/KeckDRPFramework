
from keckdrpframework.primitives.base_primitive import Base_primitive
from keckdrpframework.models.arguments import Arguments
from keckdrpframework.primitives.base_img import Base_img
from keckdrpframework.core.bokeh_plotting import bokeh_plot




class base_ccd_primitive(Base_img):

    def __init__(self, action, context):
        Base_img.__init__(self, action, context)

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

            self.logger.info(f"pre condition got {nfiles}, expecting {args.min_files}")
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


class process_bias(base_ccd_primitive):
    """
    Example using subclassing, where parameters are in action.args
    Builds a master bias frame and saves it to temp/stacked.fits with IMTYPE = "MASTER_BIAS"
    """

    def __init__(self, action, context):
        base_ccd_primitive.__init__(self, action, context)