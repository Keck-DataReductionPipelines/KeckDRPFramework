"""
Created on Jul 9, 2019

@author: skwok
"""


class Arguments(object):
    """
    This is placeholder for variables.
    """

    def __init__(self, **kargs):
        self.name = "undef"
        self.__dict__.update(kargs)

    def __str__(self):
        out = []
        for k, v in self.__dict__.items():
            out.append(f"{k}: {v}")
        return ", ".join(out)
