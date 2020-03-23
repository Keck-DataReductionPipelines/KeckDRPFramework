#!/bin/sh


#DATADIR="/net/storageserver/operations/dataArchive/k1/19/02/01"
#DATADIR="/localdata/skwok/data/deimos/19/01/30"
#DATADIR="/localdata/skwok/data/mosfire/19/05/15"
#DATADIR="/localdata/skwok/data/lris/20/01/27"

# Params: directory
doOneDir ()
{
    DATADIR=$1
    python tools/start_queue_manager.py -c config.cfg &

    PARALLEL=1

    if [ "x$PARALLEL" = 'x1' ]
    then
        sleep 3
        ./runTest_harness2.sh -o $DATADIR -w -c config.cfg &
        sleep 3
        ./runTest_harness2.sh -o $DATADIR -w -c config.cfg &
    fi
    ./runTest_harness2.sh -o $DATADIR -d $DATADIR -c config.cfg 

}

# Params: fits files
doOneFile ()
{
exec ./runTest_harness2.sh -o $DATADIR -c  config.cfg $*
}


getDirlist() 
{
#INSTLIST="deimos k1pcs kcwi lris mosfire nires nires osiris"
INSTLIST="nirspec"
for inst in $INSTLIST
do
    find /localdata/skwok/data/$inst -type d -print | while read dirname
    do
        NF=`ls -1 ${dirname}/*.fits |& wc -l`
        if [ -z "$NF" ]
        then
            continue
        fi
        if [ "$NF" -gt 5 ] 
        then
            echo "$dirname $NF"
        fi
    done
    echo 
done
}

DLIST="/localdata/skwok/data/deimos/19/02/26"

DLIST2="/localdata/skwok/data/deimos/19/02/26 \
/localdata/skwok/data/kcwi/19/07/01 \
/localdata/skwok/data/lris/20/01/27 \
/localdata/skwok/data/mosfire/19/12/14 \
/localdata/skwok/data/nires/19/09/07 \
/localdata/skwok/data/osiris/19/04/21/IMAG/raw \
/localdata/skwok/data/hires/20/02/25 \
"

for d in $DLIST
do
    doOneDir $d 
done
