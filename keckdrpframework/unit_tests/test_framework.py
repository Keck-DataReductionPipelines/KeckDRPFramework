#
# Test framework package
#
# Created: 2019-11-11, skwok
#
import pytest
import sys
from keckdrpframework.config.framework_config import ConfigClass
from keckdrpframework.core.framework import Framework
from keckdrpframework.models.processing_context import ProcessingContext
from keckdrpframework.examples.pipelines import fits2png_pipeline
from keckdrpframework.examples.pipelines.fits2png_pipeline import Fits2pngPipeline

sys.path.append("../examples")


#
# Test framework
#


def test_as_string():
    """
    pipeline is a string
    """
    cfg = ConfigClass ()
    cfg.pipeline_path = ("", "keckdrpframework.examples.pipelines")    
    f = Framework("fits2png_pipeline", cfg)
    assert f is not None


def test_as_fullpath():
    """
    pipeline is a string
    """
    f = Framework("keckdrpframework.examples.pipelines.fits2png_pipeline.Fits2pngPipeline", None)
    assert f is not None, "Could not create framework using full path as string"


def test_as_modulepath():
    """
    pipeline is a string
    """
    f = Framework("keckdrpframework.examples.pipelines.fits2png_pipeline", None)
    assert f is not None, "Could not create framework using module path as string"


def test_as_module():
    """
    pipeline is an imported module
    """
    f = Framework(fits2png_pipeline, None)
    assert f is not None, "Could not create framework using module name"


def test_as_class1():
    """
    pipeline is an imported module.class
    """
    f = Framework(Fits2pngPipeline, None)
    assert f is not None, "Could not create framework using module.class"


def test_as_class2():
    """
    pipeline is an imported class
    config is an object
    """
    cfg = ConfigClass()
    cl = fits2png_pipeline.Fits2pngPipeline
    f = Framework(cl, cfg)
    assert f is not None, "Could not create framework using class"


def test_as_object():
    """
    config is a string
    """
    context = ProcessingContext (None, None, None, ConfigClass())    
    obj = fits2png_pipeline.Fits2pngPipeline(context)
    f = Framework(obj, "example_config.cfg")
    assert f is not None, "Could not create framework using instance of class"
