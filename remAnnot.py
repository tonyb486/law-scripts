#!/usr/bin/env python3
import sys, PyPDF2

for pdf in sys.argv[1:]:
    pdfOut = PyPDF2.PdfFileWriter()
    with open(pdf, "rb") as fd:
        pdfFile = PyPDF2.PdfFileReader(fd)
        for i in range(pdfFile.getNumPages()):
            page = pdfFile.getPage(i)
            if "/Annots" in page:
                page.pop('/Annots', None)
            pdfOut.addPage(page)
        with open(pdf.replace(".pdf", ".CLEAN.pdf"), "wb") as fd:
            pdfOut.write(fd)




