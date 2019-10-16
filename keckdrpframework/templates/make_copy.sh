#!/bin/sh


changeOneFile()
{
    NAME1=$1
    FNAME=$2
    OUTFILE=$3
    sed -e 's/template/'"$NAME1"'/g' $FNAME > $OUTFILE
}

NEWNAME=`basename $1`

if [ "x$NEWNAME" = "x" ]
then 
    echo "New name expected."
    echo 
    echo "Usage: make_copy.sh  NEW_NAME"
    echo "For example: make_copy.sh projectA"
    exit 1
fi

cd ..

mkdir -p $NEWNAME
mkdir -p $NEWNAME/${NEWNAME}_pipelines
cp templates/logger.cfg README.md $NEWNAME

changeOneFile $NEWNAME templates/template_pipelines/template_pipeline.py ${NEWNAME}/${NEWNAME}_pipelines/${NEWNAME}_pipeline.py
changeOneFile $NEWNAME templates/runTest_template.sh ${NEWNAME}/runTest_${NEWNAME}.sh 
changeOneFile $NEWNAME templates/test_template.py ${NEWNAME}/test_${NEWNAME}.py
changeOneFile $NEWNAME templates/config.cfg ${NEWNAME}/config.cfg

echo
echo "../$NEWNAME created"
echo

