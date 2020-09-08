#!/usr/bin/env python3

from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
import PyPDF2, sys, tempfile

# Usage information
if len(sys.argv) != 6:
    print("Usage: %s [PDF Input] [PDF Output] [Exhibit Title] [Case Title] [Case Number]"%sys.argv[0])
    print("NOTE: Enter arguments in quotation marks if they contain spaces.")
    sys.exit(0)

# Open the PDF File and retreive the first page
pdfInput = PyPDF2.PdfFileReader(open(sys.argv[1], "rb"))
firstPage = pdfInput.getPage(0)
pageSize = firstPage.mediaBox
x,y = 18,int(pageSize[3])-54

# Generate and apply the stamp
with tempfile.NamedTemporaryFile() as tmp:
    stampCanvas = canvas.Canvas(tmp.name, pagesize=pageSize)

    stampCanvas.setFillColor(Color( 100,50,0, alpha=0.75))
    stampCanvas.roundRect(x,y,108,36, 5, fill=1)

    stampCanvas.setFillColor(Color( 0,0,0, alpha=1))
    stampCanvas.setFont("Helvetica", 12) 
    stampCanvas.drawString(x+10,y+22, sys.argv[3])

    stampCanvas.setFont("Helvetica", 7) 
    stampCanvas.drawString(x+10,y+14, sys.argv[4])
    stampCanvas.drawString(x+10,y+5, sys.argv[5])

    stampCanvas.save()

    watermark = PyPDF2.PdfFileReader(open(tmp.name, "rb"))
    firstPage.mergePage(watermark.getPage(0))

# Write the PDF to a file.
pdfOutput = PyPDF2.PdfFileWriter()
pdfOutput.addPage(firstPage)

for i in range(1,pdfInput.getNumPages()):
    pdfOutput.addPage(pdfInput.getPage(i))

with open(sys.argv[2], "wb") as fd:
    pdfOutput.write(fd)
