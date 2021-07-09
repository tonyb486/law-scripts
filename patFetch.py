#!/usr/bin/env python3

import sys, requests, tempfile
from bs4 import BeautifulSoup

# Check arguments
if len(sys.argv) < 2:
    print("Usage: %s [patent numbers]"%sys.argv[0])
    sys.exit(1)

# Fetch URL

for pat in sys.argv[1:]:
    patNum = int(pat)
    webURL = "https://pdfpiw.uspto.gov/.piw?PageNum=0&docid=%d"%(patNum)
    r = requests.get(webURL)
    s = BeautifulSoup(r.text, features="html.parser")

    # Fetch PDF itself
    pdfUrl = "https:%s"%(s.find("embed")["src"])
    with requests.get(pdfUrl) as r, open("%d.pdf"%patNum, "wb") as out:
        out.write(r.content)

    print("Saved %d.pdf"%patNum)
