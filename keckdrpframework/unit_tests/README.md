This directory contains test cases for the DRPF:

- test_config.py
- test_core.py
- test_framework.py
- test_models.py
- test\_run\_example.py
 

Command to run all unit_tests:

    pytest 
    

Or run one test, for example:

    pytest test_core.py


To skip running conftest for astropy:

    pytest --confcutdir [files]


On a successful run the output should look like this:

>> pytest --noconftest .

```
   ====================================== test session starts =======================================
   platform linux -- Python 3.7.6, pytest-5.3.2, py-1.8.1, pluggy-0.13.1
   rootdir: /net/filer2/vol/home/skwok/git/KeckDRPFramework, inifile: setup.cfg
   plugins: remotedata-0.3.2, arraydiff-0.3, hypothesis-4.54.2, doctestplus-0.5.0, openfiles-0.4.0, astropy-header-0.1.1
   collected 21 items                                                                               
   
   test_config.py .                                                                           [  4%]
   test_core.py .....                                                                         [ 28%]
   test_framework.py .......                                                                  [ 61%]
   test_models.py .......                                                                     [ 95%]
   test_run_example.py .                                                                      [100%]
  
   ====================================== 21 passed in 10.84s =======================================
```