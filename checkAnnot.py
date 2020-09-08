#!/usr/bin/env python3
import sys, PyPDF2

for pdf in sys.argv[1:]:
    with open(pdf, "rb") as fd:
        pdfFile = PyPDF2.PdfFileReader(fd)
        for i in range(pdfFile.getNumPages()):
            if "/Annots" in pdfFile.getPage(i):
                print("%s has annotation on page %d."%(pdf,i))
