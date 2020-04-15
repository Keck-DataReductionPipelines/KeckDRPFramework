#
# Clean up temporary directory
#
# Created: 2020-02-26, skwok
#
import pytest
import sys
import os
import glob


def test_clean_up():
    def remove(flist):
        for f in flist:
            os.unlink(f)

    if os.path.exists("output"):        
        remove(glob.glob("output/*.jpg"))
        os.rmdir("output")
        
    if os.path.exists("DRPF.log"):
        os.unlink ("DRPF.log")
