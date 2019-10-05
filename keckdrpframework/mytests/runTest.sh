#!/bin/sh

my_realpath() {
    BNAME=`basename $1`
    DNAME=`dirname $1`
    FDIR=`(cd $DNAME; pwd)`
    echo $FDIR/$BNAME
}

FULLPATH=`my_realpath $0`
PROGDIR=`dirname $FULLPATH`
PROGDIR=`dirname $PROGDIR`

PYTHONPATH="${PROGDIR}:${PROGDIR}/examples:${PROGDIR}/../:${PYTHONPATH}"
export PYTHONPATH

echo $PYTHONPATH $PROGDIR

python $*
