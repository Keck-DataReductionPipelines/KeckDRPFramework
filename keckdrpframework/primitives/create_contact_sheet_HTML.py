"""
Created on Jul 12, 2019
                
@author: skwok
"""

import os.path
import glob
from keckdrpframework.primitives.base_primitive import Base_primitive
from keckdrpframework.models.arguments import Arguments

class create_contact_sheet_HTML(Base_primitive):
    """
    Given a list of png files in a directory, creates a HTML file in the same directory
    containing the png files for easy viewing.
    """

    def __init__(self, action, context):
        """
        Constructor
        """    
        Base_primitive.__init__(self, action, context)
        
    
    def _genEntry (self, f):
        basename = os.path.basename(f)
        return """
        <div id="{}" style="float:left; clear:none; margin:5px">
        <img src="{}" height=256px>
        <br>
        <p>{}</p>
        </div>
        """.format (basename, basename, basename)
        
    def _perform (self):
        """
        """
        args = self.action.args
        dir_name = args.dir_name
        out_name = args.out_name
        pattern = args.pattern
        self.logger.info (f"Creating contact sheet in {dir_name}, out_name={out_name}")
        
        flist = sorted (glob.glob(dir_name + "/" + pattern))
        
        out = []
        for f in flist:
            out.append (self._genEntry (f))
        
        with open (dir_name + "/" + out_name, "w") as fh:
            print ("<html><body>", file=fh)
            print ("\n".join (out), file=fh)
            print ("</body></html>", file=fh)
        
        return Arguments()