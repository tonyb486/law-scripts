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

    #echo "Encrypting..."
    qpdf --encrypt $pw $pw 128 --use-aes=y -- "$tpdf" "Encrypted/$newpdf"
    cp "$pdf" "Original/$newpdf"
    rm "$tpdf"

done

sort $tmp/pwlist > Encrypted/pwlist.txt
