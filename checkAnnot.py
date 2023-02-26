#!/usr/bin/env python3
import sys, PyPDF2

for pdf in sys.argv[1:]:
    with open(pdf, "rb") as fd:
        pdfFile = PyPDF2.PdfReader(fd)
        for i,page in enumerate(pdfFile.pages):
            if "/Annots" in page:
                print(f"{pdf} has annotation on page {i+1}.")
