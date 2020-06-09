from keckdrpframework.primitives.base_primitive import BasePrimitive
from keckdrpframework.models.arguments import Arguments

# MODIFY the name of this class and make sure that this module/file is imported in the pipelines definition file that
# has been created in the pipeline directory


class Template2(BasePrimitive):
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

    def _pre_condition(self):
        """Check for conditions necessary to run this process"""

        some_pre_condition = True

        if some_pre_condition:
            self.logger.info("Precondition for Template2 is satisfied")
            return True
        else:
            return False

    def _post_condition(self):
        """Check for conditions necessary to verify that the process run correctly"""

        some_post_condition = True

        if some_post_condition:
            self.logger.info("Postcondition for Template2 is satisfied")
            return True
        else:
            return False

    def _perform(self):
        """
        Returns an Argument() with the parameters that depends on this operation.
        """

        # do something with self.args
        self.logger.info("Running action Template2")
        return self.action.args
