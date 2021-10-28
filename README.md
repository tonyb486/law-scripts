These are a few scripts that I have used in law practice to automate tasks that are tedious and error-prone to perform manually.  They're short, quick hacks that I find effective with some manual checking and intervention.  They should all be considered experimental.

These scripts are released AS-IS with ABSOLUTELY NO WARRANTY under the MIT license.  See the `LICENSE` file for details. Whenever I use them, I manually check the output to make sure it is sensible.

## patFetchFH.py

`usage: patFetchFH.py <Patent Number>`

Fetches the file history for a patent using the [PEDS API](https://ped.uspto.gov/peds/#!/) and the [IFW/CMS Archive](https://developer.uspto.gov/data/pair-archives) from the USPTO.  May differ from the file history available on PAIR, and may be updated at different times.

Dependencies: Python (3.x), PyPDF2.

## patFamilyTree.py

`usage: patFamilyTree.py [-h] [--first] patent`

`example: patFamilyTree.py <patent number> | dot -Tpdf > tree.pdf`

A tool used for attempting to generate patent family trees.  Uses data from the [PEDS API](https://ped.uspto.gov/peds/#!/) from the USPTO.  It outputs data in the [dot](https://graphviz.org/doc/info/lang.html) format for use with [graphviz](https://graphviz.org/), which is required to actually generate a document.  It's still sloppy, and its output should be checked manually.  Use the `--first` option to only include an edge on the graph for the latest-filed parent of each application, and the first child application if applicable, which may greatly simplify more complicated family trees while still conveying the necessary information.

Dependencies: Python (3.x), Graphviz.

## patFetch.py

`usage: patFetch.py [patents...]`

A tool used to fetch multiple patents from the USPTO PatFT.  Uses a small amount of screenscraping, so this script could break, and requires BeautifulSoup (bs4)$$.  Takes a list of patent numbers as arguments, saves PDFs with the patent numbner.

Dependencies: Python (3.x), BeautifulSoup (bs4)

## checkAnnot.py

`usage: checkAnnot.py <PDF Files>`

This script will check for the presence of a PDF annotation layer(highlights, etc.) in a PDF file, and echo the pages that have such a layer.  I use it to check that I've successfully removed all annotations before I send a file for printing.  It is also useful for finding pages that have annotations on them in many file and listing them to be flagged when printed out.  **WARNING: It may miss annotations that are flattend into a file**.

Dependencies: Python (3.x), PyPDF2.

## remAnnot.py

`usage: remAnnot.py <PDF Files>`

This script will *remove* the PDF annotation layer (highlights, etc.) in a PDF file.  I use it to remove all annotations before I send a file for printing.  **WARNING: It may miss annotations that are flattend into a file. Always manually check the output when removing annotations is crucial.**

Dependencies: Python (3.x), PyPDF2.

## encryptDocs.sh

`usage: encryptDocs.sh <PDF files>`

This script will create a folder `Encrypted` containing PDFs encrypted with random passwords using PDF encryption (AES, 128-bit, Acrobat Reader 7.0+).  It will create a file `pwlist.txt` listing the passwords for each file.

Dependencies: UNIX Shell (I use zsh or bash), qpdf, pwgen.

## stampLabel.py

`usage: stampLabel.py [PDF Input] [PDF Output] [Exhibit Title] [Case Title] [Case Number]`

This script will add a yellow exhibit stamp to a PDF file in the top-left corner.  The exhibit stamp contains the title (*e.g.*, Exhibit A), and room for the case title and the case number below it.  As with any shell invocation, enter arguments in quotes if they contain spaces.

Dependencies: Python (3.x), PyPDF2, Reportlab.

## depo2html.py

`usage: depo2html.py  [ASCII Deposition File] [HTML Output File]`

This is a (somewhat sloppy) script that attempts to reformat an ASCII deposition file into a more easily readable HTML file.  It's just a quick and dirty set of regular expressions, so your mileage may vary, but I find it much easier to read in this format than the original formatting. I plan to
completely rewrite this at some point/

Dependencies: Python (3.x).

## pdfBates.sh

`usage: ./pdfBates.sh [Starting Bates Number with Prefix] [Path to PDF Files...]`

Renders a PDF to flat 300dpi monochrome images using imagemagick, adds sequential page numbers, and compresses it down to a PDF with jbig2enc to reduce the file size.  This is kind of a hacky multithreaded shell script, so it might fail dramatically.

Dependencies: [jbig2enc](https://github.com/agl/jbig2enc), [imagemagick](https://imagemagick.org/index.php), [ghostscript](https://www.ghostscript.com/)

## pdfFlat.sh

`usage: ./pdfFlat.sh [Path to PDF Files...]`

Renders a PDF to flat 300dpi JPEG images using ghostscript, and then uses img2pdf to mash them
together into a letter-sized PDF file. Also uses exiftools on the JPEGs. Used to approximate 
the process of printing and scanning.

Dependencies: [ghostscript](https://www.ghostscript.com/), [img2pdf](https://pypi.org/project/img2pdf/); Optional: [jpegoptim](https://github.com/tjko/jpegoptim), [exiftool](https://exiftool.org/)