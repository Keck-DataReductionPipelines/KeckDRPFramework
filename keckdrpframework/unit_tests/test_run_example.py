#
# Test running the example 
#
# Created: 2019-11-22, skwok
#
import pytest
import sys
import glob
import time
sys.path.extend (("../", "../..", "../examples"))

from keckdrpframework.config.framework_config import ConfigClass
from keckdrpframework.core.framework import Framework
from keckdrpframework.models.event import Event
from keckdrpframework.examples.pipelines.fits2png_pipeline import Fits2pngPipeline


def test_run_example():
    f = Framework(Fits2pngPipeline, "example_config.cfg")    
    assert f is not None, "Could not create framework"
    
    f.config.no_event_event = Event("no_event", None)
    f.config.fits2png = ConfigClass ("../examples/fits2png.cfg")
    f.ingest_data("test_files", ())
    f.start_action_loop  ()
    
    for i in range (10):
        time.sleep(2)
        q1sz, q2sz = f.get_pending_events()
        if len(q1sz) == 0 and len(q2sz) == 0: 
            break
        
    flist = glob.glob("output/*.jpg")
    assert len(flist) == 6, "Unexpected number of files"
    
    
