"""
Ingests files from a given directory
                
Created 2019-09-05
@author: skwok
"""

import os
import glob

from keckdrpframework.models.arguments import Arguments
from keckdrpframework.primitives.base_primitive import BasePrimitive


class IngestFiles(BasePrimitive):
    """
    Ingest files from a given directory
    """

    def __init__(self, action, context):
        """
        Constructor
        """
        BasePrimitive.__init__(self, action, context)

    def _perform(self):
        """
        Expects name, extension, associate_event as arguments.
        
        Adds associate event for each file in directory name with given extension.
        """
        path = self.name
        ext = self.extension
        event = self.associate_event
        queue = self.context.event_queue
        if os.path.isdir(path):
            flist = glob.glob(path + "/*." + ext)
            for f in flist:
                args = Arguments(name=f)
                queue.put(event, args)
        else:
            args = Arguments(name=path)
            queue.put(event, args)

        return Argument()
