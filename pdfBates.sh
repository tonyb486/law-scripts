#!/usr/bin/env bash

# Edit if you want to use more threads, or if jbig2enc is installed somewhere else.
#
# Ten threads makes my M1 Macbook Air warm to the touch with native arm64 binaries of
# imagemagick and jbig2enc.
#
PDFTHREADS=10
JBIG2PATH=

# No more edit unless broken.
TMPDIR=$(mktemp -d)
BATES_PREFIX=$(echo $1 | sed 's/[0-9]*$//')
BATES=$(echo $1 | sed 's/^'$BATES_PREFIX'//')
BATES=$((10#$BATES+0))

if [ ! -z $BATES_PREFIX ]; then
    echo "Using bates prefix $BATES_PREFIX and starting from $BATES_PREFIX$BATES"
fi

while test ${#} -gt 1
do
    shift # Iterate to next arg
    PDF=$1

    # Process a PDF
    OUTFILE=$(printf "$BATES_PREFIX%05d.pdf" $BATES)
    PAGECOUNT=$(qpdf --show-npages "$PDF")
    echo "Processing $PDF with $PAGECOUNT pages into $OUTFILE"

    # process in chunks of $PDFTHREADS for the rendering step.
    for x in `seq 0 $PDFTHREADS $PAGECOUNT`; do
        for i in `seq $x $(($x+$PDFTHREADS-1))`; do
            if [ $i -lt $PAGECOUNT ]; then
                if [ -z $BATES_PREFIX ]; then
                    convert -density 300 -monochrome -depth 1 "$PDF[$i]" \
                    $TMPDIR/TMPIMG-%03d.png &
                else 
                    convert -density 300 -monochrome -depth 1 "$PDF[$i]" \
                            -gravity southeast -annotate 0 "$(printf "$BATES_PREFIX%05d" $BATES)" \
                            $TMPDIR/TMPIMG-%03d.png &

                echo -n "...$(($i+1))"
                BATES=$(($BATES+1))
                fi
            fi
        done
        wait # wait until the 10 pages have rendered.
    done

    echo "....."

    "$JBIG2PATH"jbig2 -b $TMPDIR/output -s -p -v $TMPDIR/TMPIMG-*.png 2>/dev/null
    "$JBIG2PATH"pdf.py $TMPDIR/output > $OUTFILE
    rm $TMPDIR/TMPIMG*
    rm $TMPDIR/output*

done