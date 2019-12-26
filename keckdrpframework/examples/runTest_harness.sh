#!/bin/sh

#
# Script wrapper for test_harness.py
#
# Created: 2019-09-30, skwok
#

my_realpath() {
    BNAME=`basename $1`
    DNAME=`dirname $1`
    FDIR=`(cd $DNAME; pwd)`
    echo $FDIR/$BNAME
}

FULLPATH=`my_realpath $0`
PROGDIR=`dirname $FULLPATH`
PROGDIR1=`dirname $PROGDIR`
PROGDIR2=`dirname $PROGDIR1`

PYTHONPATH=".:${PROGDIR1}:${PROGDIR2}:${PYTHONPATH}"
export PYTHONPATH

echo $PYTHONPATH

# For example:
# 
# sh runTest_harness.sh fits2png_pipeline config.cfg -d ../unit_tests/test_files
#

\rm -rf output/*.png output/test.html
python test_harness.py $*
