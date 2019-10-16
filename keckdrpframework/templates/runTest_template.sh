#!/bin/sh

#
# Script wrapper for test_template.py
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

python test_template.py template_pipeline config.cfg $*
