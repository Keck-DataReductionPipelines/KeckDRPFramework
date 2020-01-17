#
# Test running the example 
#
# Created: 2019-11-22, skwok
#
import pytest
import sys
import glob

sys.path.extend (("../examples", ".."))

from keckdrpframework.config.framework_config import ConfigClass
from keckdrpframework.core.framework import Framework
from keckdrpframework.examples.pipelines.fits2png_pipeline import Fits2pngPipeline


def test_run_example():
    f = Framework(Fits2pngPipeline, "example_config.cfg")
    assert f is not None, "Could not create framework"
    f.config.fits2png = ConfigClass ("../examples/fits2png.cfg")
    f.ingest_data("test_files", ())
    f.start (qm_only=False,  ingest_data_only=False, wait_for_event=False, continuous=False)
    
    flist = glob.glob("output/*.png")
    assert len(flist) == 6, "Unexpected number of files"
    
    
