#!/usr/bin/env python3

import sys, requests, tempfile
from bs4 import BeautifulSoup

# Check arguments
if len(sys.argv) < 2:
    print("Usage: %s [patent numbers]"%sys.argv[0])
    sys.exit(1)

# Fetch URL

for pat in sys.argv[1:]:
    patNum =  "D%07d"%(int(pat[1:])) if pat[0] == "D" else str(int(pat))
    webURL = "https://pdfpiw.uspto.gov/.piw?PageNum=0&docid=%s"%(patNum)
    r = requests.get(webURL)
    s = BeautifulSoup(r.text, features="html.parser")

    # Fetch PDF itself
    pdfUrl = "https:%s"%(s.find("embed")["src"])
    with requests.get(pdfUrl) as r, open("%s.pdf"%patNum, "wb") as out:
        out.write(r.content)

    print("Saved %s.pdf"%patNum)
