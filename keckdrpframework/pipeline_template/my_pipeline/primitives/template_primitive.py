from keckdrpframework.primitives.base_primitive import BasePrimitive
from keckdrpframework.models.arguments import Arguments
from keckdrpframework.primitives.base_img import BaseImg

from keckdrpframework.primitives.base_primitive import BasePrimitive

# MODIFY the name of this class and make sure that this module/file is imported in the pipelines definition file that
# has been created in the pipeline directory

class Template(BasePrimitive):
    """
    This is a template for primitives, which is usually an action.

    The methods in the base class can be overloaded:
    - _pre_condition
    - _post_condition
    - _perform
    - apply
    - __call__
    """

    def __init__(self, action, context):
        """
        Constructor
        """
        BasePrimitive.__init__(self, action, context)


    def _perform (self):
        """
        Returns an Argument() with the parameters that depends on this operation.
        """
        raise Exception ("Not yet implemented")