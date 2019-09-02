#!/bin/sh

FULLPATH=`readlink -f $0`
PROGDIR=`dirname $FULLPATH`
PROGDIR=`dirname $PROGDIR`

PYTHONPATH="$PROGDIR:$PYTHONPATH"
export PYTHONPATH

echo $PYTHONPATH $PROGDIR

PYTHON="python"

TESTDATADIR="../../test_fits/HIRES"


runTest() {
    $PYTHON $*
}




runTest test_framework.py

runTest test_fits2png.py $TESTDATADIR
runTest test_fits2png_with_actions.py $TESTDATADIR
runTest test_fits2png_server.py $TESTDATADIR
