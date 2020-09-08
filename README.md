# Various Scripts

These are a few scripts that I have used in law practice to automate tasks that are tedious and error-prone to perform manually.  They mostly relate to PDF files. 

These scripts are released AS-IS with ABSOLUTELY NO WARRANTY under the MIT license.  See the `LICENSE` file for details. Whenever I use them, I manually check the output to make sure it is sensible.

## checkAnnot.py

`Usage: checkAnnot.py <PDF Files>`

This script will check for the presence of a PDF annotation layer(highlights, etc.) in a PDF file, and echo the pages that have such a layer.  I use it to check that I've successfully removed all annotations before I send a file for printing.  **WARNING: It may miss annotations that are flattend into the file**.

Dependencies: Python (3.x), PyPDF2.

## remAnnot.py

`Usage: remAnnot.py <PDF Files>`

This script will *remove* the PDF annotation layer (highlights, etc.) in a PDF file.  I use it to remove all annotations before I send a file for printing.  **WARNING: It may miss annotations that are flattend into the file. Always manually check before use.**.

Dependencies: Python (3.x), PyPDF2.

## encrypt.sh

`Usage: encrypt.sh <PDF files>`

This script will create a folder `Encrypted` containing PDFs encrypted with random passwords using PDF encryption (AES, 128-bit, Acrobat Reader 7.0+).  It will create a file `pwlist.txt` listing the passwords for each file.

Dependencies: UNIX Shell (I use zsh or bash), qpdf, pwgen.




