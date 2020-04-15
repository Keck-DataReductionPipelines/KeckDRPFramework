#
# Test Recurrent events
# 
#
# Created: 2020-04-14, skwok
#
import pytest
import sys

sys.path.append ("../..")

from keckdrpframework.config.framework_config import ConfigClass
from keckdrpframework.core.framework import Framework
from keckdrpframework.utils.drpf_logger import getLogger
from keckdrpframework.models.event import Event
from keckdrpframework.models.arguments import Arguments
from keckdrpframework.examples.pipelines.fits2png_pipeline import Fits2pngPipeline

@pytest.fixture
def init_framework ():
    """
    Initializes frame work for testing.
    This is an non-multiprocessing framework. See example_config.cfg.
    The pipeline 'Fits2pngPipeline' is imported. See test_framework.py for other options.
    """
    f = Framework(Fits2pngPipeline, "example_config.cfg")    
    assert f is not None, "Could not create framework"
    
    f.config.no_event_event = None #Event("no_event", None)
    f.config.fits2png = ConfigClass ("../examples/fits2png.cfg")
    return f

   
def test_recurrent_1 (init_framework):
    f = init_framework

    f.append_event("no_event", Arguments(name="dummy1"), recurrent=True)
    f.append_event("no_event", Arguments(name="dummy2"), recurrent=True)

    f.main_loop()
    
    in_progress = f.event_queue.get_in_progress ()
    print (len(in_progress))
    assert len(in_progress) == 0, f"Unexpected events in progress, should be none"



