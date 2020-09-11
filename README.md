These are a few scripts that I have used in law practice to automate tasks that are tedious and error-prone to perform manually.  They mostly relate to PDF files. 

These scripts are released AS-IS with ABSOLUTELY NO WARRANTY under the MIT license.  See the `LICENSE` file for details. Whenever I use them, I manually check the output to make sure it is sensible.

## checkAnnot.py

`Usage: checkAnnot.py <PDF Files>`

This script will check for the presence of a PDF annotation layer(highlights, etc.) in a PDF file, and echo the pages that have such a layer.  I use it to check that I've successfully removed all annotations before I send a file for printing.  It is also useful for finding pages that have annotations on them in many file and listing them to be flagged when printed out.  **WARNING: It may miss annotations that are flattend into a file**.

Dependencies: Python (3.x), PyPDF2.

## remAnnot.py

`Usage: remAnnot.py <PDF Files>`

This script will *remove* the PDF annotation layer (highlights, etc.) in a PDF file.  I use it to remove all annotations before I send a file for printing.  **WARNING: It may miss annotations that are flattend into a file. Always manually check the output when removing annotations is crucial.**

Dependencies: Python (3.x), PyPDF2.

## encryptDocs.sh

`Usage: encryptDocs.sh <PDF files>`

This script will create a folder `Encrypted` containing PDFs encrypted with random passwords using PDF encryption (AES, 128-bit, Acrobat Reader 7.0+).  It will create a file `pwlist.txt` listing the passwords for each file.

Dependencies: UNIX Shell (I use zsh or bash), qpdf, pwgen.

## stampLabel.py

`Usage: stampLabel.py [PDF Input] [PDF Output] [Exhibit Title] [Case Title] [Case Number]`

This script will add a yellow exhibit stamp to a PDF file in the top-left corner.  The exhibit stamp contains the title (*e.g.*, Exhibit A), and room for the case title and the case number below it.  As with any shell invocation, enter arguments in quotes if they contain spaces.

Dependencies: Python (3.x), PyPDF2, Reportlab.

## depo2html.py

`Usage: depo2html.py  [ASCII Deposition File] [HTML Output File]`

This is a (somewhat sloppy) script that attempts to reformat an ASCII deposition file into a more easily readable HTML file.  It's just a quick and dirty set of regular expressions, so your mileage may vary, but I find it much easier to read in this format than the original formatting.

Dependencies: Python (3.x).
