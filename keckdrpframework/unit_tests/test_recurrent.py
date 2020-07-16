#
# Test Recurrent events
# 
#
# Created: 2020-04-14, skwok
#
import pytest
import sys

sys.path.append ("../..")

from keckdrpframework.core.framework import Framework
from keckdrpframework.models.arguments import Arguments

from keckdrpframework.pipelines.base_pipeline import BasePipeline


class SimplePipeline (BasePipeline):    
    # name: ("action_name", "new state", "next event")
    event_table = {"test_event1": ("test_action1", "state1", None), 
    "test_event2": ("test_action2", "state2", None)}

    def __init__(self, context):
        super(SimplePipeline, self).__init__(context)
        context.counter1 = 0
        context.counter2 = 0

    def test_action1 (self, action, context):
        context.counter1 += 1
        if context.counter1 >= action.args.maxVal: 
            action.event._recurrent = False
        return None
    
    def test_action2 (self, action, context):
        context.counter2 += 1
        if context.counter2 >= action.args.maxVal: 
            action.event._recurrent = False
        return None

@pytest.fixture
def init_framework ():
    """
    Initializes frame work for testing.
    This is an non-multiprocessing framework. See example_config.cfg.
    The pipeline 'Fits2pngPipeline' is imported. See test_framework.py for other options.
    """
    f = Framework(SimplePipeline, "example_config.cfg")    
    assert f is not None, "Could not create framework"
    
    f.config.no_event_event = None
    return f

   
def test_recurrent_1 (init_framework):
    f = init_framework

    max1 = 4
    max2 = 7
    f.append_event("test_event1", Arguments(name="dummy1", maxVal=max1), recurrent=True)
    f.append_event("test_event2", Arguments(name="dummy2", maxVal=max2), recurrent=True)

    f.main_loop()
    
    assert f.context.counter1 == max1, f"Counter1 mismatch, expectd {max1}, got {f.context.counter1}"
    assert f.context.counter2 == max2, f"Counter1 mismatch, expectd {max2}, got {f.context.counter2}"




