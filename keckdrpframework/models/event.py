"""
Created on Jul 8, 2019

@author: skwok
"""


class Event(object):
    """
    The event object.
    Contains an index to keep them sorted.
    """

    def __init__(self, name, args):
        """
        Constructor
        """
        self.name = name
        self.args = args

    def __str__(self):
        return f"Event {self.name}, args={self.args}"
