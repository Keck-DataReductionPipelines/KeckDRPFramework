#
# Test running configugration
#
# Created: 2019-12-18, skwok
#
import pytest
import sys

sys.path.append("../..")
from keckdrpframework.config.framework_config import ConfigClass
from keckdrpframework.core.framework import Framework
from keckdrpframework.examples.pipelines.fits2png_pipeline import Fits2pngPipeline


def test_config1():
    """
    Reads simple config file in examples_config.cfg
    """
    cfg = ConfigClass("examples_config.cfg")
    assert cfg.file_type == "*.fits", f"Unexpected value for file_type ({cfg.file_type}), expected '*.fits'"


def test_config2():
    """
    Reads config with custom default section
    """
    cfg = ConfigClass("my_config.cfg", default_section="CUSTOM")
    assert cfg.test_property == "test", f"Unexpected config property value, got {cfg.test_property}"
