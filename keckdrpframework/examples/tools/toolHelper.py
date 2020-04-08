
import sys
import os

def import_module (mod_name):
    """
    Traverse the full path of this file to find the desired module name.
    Then import that desired module.

    For example:        
        from toolHelper import import_module
        import_module ("keckdrpframework")

    """
    realpath = os.path.realpath(__file__)
    parts = realpath.split(os.path.sep)
    for i, p in enumerate(parts):
        if p == mod_name:
            sys.path.append (os.path.sep.join (parts[:i]))
            break
