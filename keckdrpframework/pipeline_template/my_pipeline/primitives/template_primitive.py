from keckdrpframework.primitives.base_primitive import Base_primitive
from keckdrpframework.models.arguments import Arguments
from keckdrpframework.primitives.base_img import Base_img

from keckdrpframework.primitives.base_primitive import Base_primitive

class Template(Base_primitive):
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
        Base_primitive.__init__(self, action, context)


    def _perform (self):
        """
        Returns an Argument() with the parameters that depends on this operation.
        """
        raise Exception ("Not yet implemented")