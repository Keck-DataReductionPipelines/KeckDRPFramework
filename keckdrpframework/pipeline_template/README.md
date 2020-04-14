# Template Pipeline

This directory contains a skeleton pipeline that can be used to start developing a new pipeline.

### Do not change anything in this directory.
Instead, make a copy of this directory and rename it appropriately according to your project.

To use this template, first create a directory for your new pipeline package

For example:

    mkdir MyPipeline
    
Copy the template in the directory just created:

    cp -r <KeckDRPFramework_location>/keckdrpframework/templates/* .

Change the directory names accordingly:

    mv my_pipeline <your_project_name>
    
Modify the setup.py file with the appropriate names for your drp.

Modify at the pipelines/template_pipeline.py to give a name to your pipeline, replacing "template_pipeline"

Make sure that the pipeline class you just created is imported correctly by the template script in the scripts directory

You can then install your new pipeline:

    python setup.py develop
    
And start the processing with the script:

    template_script arg1 args2 ....
    
