#!/usr/bin/env bash


# No more edit unless broken.
TMPDIR=$(mktemp -d)

while test ${#} -gt 0
do
    PDF=$1

    # Process a PDF
    OUTFILE="$PDF".flat.pdf
    PAGECOUNT=$(qpdf --show-npages "$PDF")
    echo "Processing $PDF with $PAGECOUNT pages into $OUTFILE"

    gs -dBATCH -dNOPAUSE -dNumRenderingThreads=10 -sDEVICE=jpeg -dJPEGQ=70 -r300 -dUseCropBox -sOutputFile=$TMPDIR/TMPIMG-%04d.jpg "$PDF"

    if command -v jpegoptim
    then
        echo "Strip EXIF..."
        for i in $TMPDIR/TMPIMG*
        do
            echo -n "."
            exiftool -all= $i
        done
    fi

    if command -v jpegoptim
    then
        echo "Apply jpegoptim..."
        for i in $TMPDIR/TMPIMG*
        do
            echo -n "."
            jpegoptim -s $i
        done
    fi

    echo "....."
    
    img2pdf -a --output "$OUTFILE" --pagesize Letter $TMPDIR/TMPIMG-*.jpg
    rm $TMPDIR/TMPIMG*

    shift # Iterate to next arg
done



