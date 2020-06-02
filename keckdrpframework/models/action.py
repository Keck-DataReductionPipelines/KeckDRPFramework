"""
Created on Jul 8, 2019

@author: skwok
"""


class Action:
    """
    Action, represents action to pass to a primitive.
    Action Constructor:
        Action (eventt_info, args)
        event_info: a tuple (action_name, state_name, next_event)
        args: Arguments (key1=val1, key2=val2, ...)
    """

    def __init__(self, event, event_info, args):
        """
        Action Constructor:
        event_info: a tuple (action_name, state_name, next_event)
        args: Arguments (key1=val1, key2=val2, ...)
        """
        self.event = event
        self.name, self.next_state, self.new_event = event_info
        self.args = args
        self.output = None

    def __str__(self):
        return f"{self.name}, {self.args}, {self.next_state}, {self.new_event}"
