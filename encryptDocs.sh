#!/bin/bash

mkdir Encrypted Original 
tmp=$(mktemp -d)

find . -iname "*.pdf" -maxdepth 1 | while read pdf
do

    echo $pdf

    tpdf=$tmp/"$(basename "$pdf")"
    cp "$pdf" "$tpdf"

    pw=$(pwgen $(( ( RANDOM % 5 )  + 10 )) 1)
    newpdf="$(basename "$pdf" | sed 's/\..*/.pdf/')"
    echo $newpdf: "$pw" >> $tmp/pwlist

    # Note for below:
    # Change '256' to '128' if someone can't handle 256-bit encryption.
    #
    # For some reason, Microsoft Edge is the default Windows 10 PDF viewer,
    # and it can't handle 256-bit AES.
    #
    
    qpdf --encrypt $pw $pw 256 --use-aes=y -- "$tpdf" "Encrypted/$newpdf"
    cp "$pdf" "Original/$newpdf"
    rm "$tpdf"

done

sort $tmp/pwlist > Encrypted/pwlist.txt
