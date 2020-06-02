"""
Created on Jul 8, 2019

@author: skwok
"""

import uuid
import datetime


class Event(object):
    """
    The event object.
    Contains an index to keep them sorted.
    """

    counter = 0

    def __init__(self, name, args, recurrent=False):
        """
        This class represents the an event, which solicitates an action.
        The association of an event to the wanted action is defined somewhere,
        for example in the pipeline.

        An recurrent event is an event that is re-issued after it is handled.
        For example, a periodic tasks can be implemented using recurrent events.

        Args:
            name: name of the event
            args: user data passed to the event
            recurrent: indicates if this event is a recurrent event.

        """
        self.id = uuid.uuid1(clock_seq=self.counter).hex
        self.counter += 1
        self.name = self.id if name is None else name
        self.args = args

        self._recurrent = recurrent
        self._timestamp = datetime.datetime.utcnow()

    def __str__(self):
        return f"Event {self.name}, args={self.args}"

    def set_recurrent(self, recurrent=False):
        self._recurrent = recurrent
