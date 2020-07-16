#
# Test running the example 
#
# Created: 2019-11-22, skwok
#
import pytest
import sys
import glob
import time
import os

sys.path.extend (("../", "../..", "../examples"))

from keckdrpframework.config.framework_config import ConfigClass
from keckdrpframework.core.framework import Framework
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
    
    f.config.no_event_event = None # Make sure the loop terminates
    f.config.fits2png = ConfigClass ("../examples/fits2png.cfg")
    return f


def test_run_example(init_framework):
    """
    Tests ingesting files from a directory, ie. test_files.
    The events are pushed to the event queue.
    main_loop() processes the events.
    At the end there should be 6 JPG files in the output directory.
    """
    f = init_framework
    f.ingest_data("test_files", ())
    f.main_loop()
        
    flist = glob.glob("output/*.jpg")
    assert len(flist) == 6, f"Unexpected number of files, expected {6}, got {len(flist)}"
    
    
def test_run_example_2(init_framework):
    f = init_framework
    
    infile = "test_files/571_0001.fits"
    outfile = "output/571_0001.jpg"

    if os.path.isfile(outfile): os.unlink (outfile)
    f.ingest_data(None, [infile])

    f.main_loop()
        
    assert os.path.isfile(outfile), f"Output file {outfile} missing"

   
def test_run_example_3(init_framework):
    f = init_framework

    flist = glob.glob("test_files/*.fits")

    for fn in flist:
        f.append_event("next_file", Arguments(name=fn))

    f.main_loop()
        
    flist = glob.glob("output/*.jpg")
    assert len(flist) == 6, f"Unexpected number of files, expected {6}, got {len(flist)}"
    
    in_progress = f.event_queue.get_in_progress ()
    print (len(in_progress))
    assert len(in_progress) == 0, f"Unexpected events in progress, should be none"

def test_terminate (init_framework):
    f = init_framework
    qsz1, hiqsz = f.get_pending_events ()
    assert len(hiqsz) == 0, "Unexpected items in high priority event queue"
    assert len(qsz1) == 0, "Unexpected items in event queue"
    
