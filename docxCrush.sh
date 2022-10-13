#!/usr/bin/env bash

# temp directory
DOCXDIR="$(mktemp -d)"

# Extract
7zz x $1 -o$DOCXDIR

# Change to dir and do stuff
cd "$DOCXDIR"
for i in word/media/*; do
    if [[ "$i" != *.jpeg ]]; then
        NEWNAME=$(echo "$i" | sed 's/\.[^\.]*/\.jpeg/')
        convert -quality 85 "$i" "$NEWNAME"
        rm "$i"

        NEWFILE=$(basename "$NEWNAME")
        OLDFILE=$(basename "$i")

        gsed -i "s/$OLDFILE/$NEWFILE/" "word/_rels/document.xml.rels"

    fi
done

7zz a output.zip .

cd -
cp "$DOCXDIR"/output.zip $1.small.docx
rm -rf "$DOCXDIR"
