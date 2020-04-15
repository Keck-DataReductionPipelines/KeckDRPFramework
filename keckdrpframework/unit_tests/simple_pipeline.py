#
# Simple pipeline for testing.
# Don't call this file test_pipeline to avoid pytest taking this as a test case.
#
# Created: 2020-04-15, skwok

import time
from keckdrpframework.pipelines.base_pipeline import BasePipeline


class SimplePipeline (BasePipeline):    
    # name: ("action_name", "new state", "next event")
    event_table = {"test_event1": ("test_action1", "state1", None), 
    "test_event2": ("test_action2", "state2", None)}

    def __init__(self, context):
        super(SimplePipeline, self).__init__(context)
        self.counter1 = 0
        self.counter2 = 0

    def test_action1 (self, action, context):
        self.counter1 += 1
        if self.counter1 > 3: 
            action.event._recurrent = False
        time.sleep (1)
        return None
    
    def test_action2 (self, action, context):
        self.counter2 += 1
        if self.counter2 > 7: 
            action.event._recurrent = False
            time.sleep (1)
        return None

