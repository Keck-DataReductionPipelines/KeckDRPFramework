.. _arguments:

Arguments
=========
The ``Arguments`` class provides a flexible way to store any argument that need to be passed to functions or classes.
Other pipeline frameworks have adopted a rather well-defined data model, using arrays or more sophisticated data
structures to store FITS files or tables.

For this framework, we have opted for the maximum flexibility.

An example of using the concept of ``arguments`` is the way that we process the Keck Cosmic Web Imager (KCWI) data. For
this instrument, the raw FITS file is made of two extensions: the actual CCD data and a table listing the shutter
open/close events with timestamps.

To read this type of FITS files, we can define a specific FITS reader for KCWI as:

.. code-block:: python

 def kcwi_fits_reader(file):
    """A reader for KeckData objects.
    """
    hdul = fits.open(file)

    if len(hdul) == 2:
        # 1- read the first extension into a ccddata
        ccddata = CCDData(hdul[0].data, meta=hdul[0].header, unit='adu')
        # 2- read the table
        table = hdul[1]

We can then create a primitive that can take care of ingesting a KCWI FITS file by subclassing the ``Base_primitive``
as described in the previous section:

.. code-block:: python

 class kcwi_fits_ingest(Base_primitive):

     def __init__(self, action, context):
         '''
         Constructor
         '''
         Base_primitive.__init__(self, action, context)

     def _perform(self):
         '''
         Expects action.args.name as fits file name
         Returns HDUs or (later) data model
         '''
         name = self.action.args.name
         self.logger.info(f"Reading {name}")
         out_args = Arguments()
         out_args.name = name
         ccddata, table = self.kcwi_fits_reader(name)
         out_args.ccddata = ccddata
         out_args.table = table
         out_args.imtype = out_args.hdus.header['IMTYPE']

         return out_args

Note that the name of the file is passed to this function as part of the ``action`` dictionary. We will describe
this dictionary later.
The relevant code is the construction of the ``out_args`` variable: first, it is instantiated as  ``Arguments``, then
it is populated with various elements such as an Astropy NDData CCDData object for the CCD data, and a table. Finally,
and just for convenience, the image type is extracted from the header and assigned to the ``imtype`` property of
the class.

By doing this, we have effectively defined our own KCWI data model as being composed of a CCDData object, plus a table,
plus additional extracted information such as the image type.