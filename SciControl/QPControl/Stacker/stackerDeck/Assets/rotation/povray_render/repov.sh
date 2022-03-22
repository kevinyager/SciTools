#!/bin/bash

export POVRAY_BETA=703742214

#FILE_BASE="diagram"
FILE_BASE=$1

LAST_DATE=0

while [ 1 ] 
do

  CUR_DATE=`stat -c %Y $FILE_BASE.pov`

  if [ $CUR_DATE -gt $LAST_DATE ]; then
    echo "POV-Ray file modified..."
    LAST_DATE=$CUR_DATE

    # Re-render
    povray povray.ini +I$1.pov

    # Convert
    #convert $1.tga $1.png

    # Crop
    #convert $1.tga -crop 420x420+180+110 $1.png

  fi

  sleep 1

done
