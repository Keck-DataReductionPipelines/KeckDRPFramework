#
# Test framework package
#
# Created: 2019-11-11, skwok
#
import pytest
import sys
from keckdrpframework.config.framework_config import ConfigClass
from keckdrpframework.core.framework import Framework
from keckdrpframework.examples.pipelines import fits2png_pipeline

sys.path.append ("../examples")


#
# Test framework
#

def test_as_string ():
    """
    pipeline is a string
    """
    f = Framework ('fits2png_pipeline', None)
    assert (f is not None)
    
    
def test_as_module ():
    """
    pipeline is an imported module
    """
    f = Framework (fits2png_pipeline, None)    
    assert (f is not None)
    
    
def test_as_class ():
    """
    config is an object
    """
    cfg = ConfigClass ()
    cl = fits2png_pipeline.fits2png_pipeline
    f = Framework (cl, cfg)    
    assert (f is not None)
    
    
def test_as_object ():
    """
    config is a string
    """
    obj = fits2png_pipeline.fits2png_pipeline()
    f = Framework (obj, "../examples/config.cfg")    
    assert (f is not None)

