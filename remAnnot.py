#!/usr/bin/env python3
import sys, PyPDF2

for pdf in sys.argv[1:]:
    pdfOut = PyPDF2.PdfWriter()
    with open(pdf, "rb") as fd:
        pdfFile = PyPDF2.PdfReader(fd)
        for i,page in enumerate(pdfFile.pages):
            if "/Annots" in page:
                page.pop('/Annots', None)
                print(f"{pdf}: Removed annotation on page {i+1}.")
            pdfOut.add_page(page)
        with open(pdf.replace(".pdf", ".CLEAN.pdf"), "wb") as fd:
            pdfOut.write(fd)



