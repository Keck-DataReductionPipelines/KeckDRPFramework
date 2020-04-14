"""
Created on Jul 10, 2019

@author: skwok
"""

import traceback


def tryEx(f):
    def ff(*args, **kargs):
        try:
            return f(*args, **kargs)
        except:
            traceback.print_exc()

    return ff
