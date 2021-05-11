#!/usr/bin/env python3

import sys, requests, json, zipfile, io, datetime, PyPDF2
import xml.etree.ElementTree as ET

# Check arguments
if len(sys.argv) != 2:
    print("Usage: %s [patent number]"%sys.argv[0])
    sys.exit(1)

patNum = sys.argv[1]

# Load document code names
with open("/Users/tonyb/.local/share/docCodes.json", "r") as t: 
    docCodes = json.loads(t.read())

# Search for the application by patent number
print("Searching for patent.")

q = {"searchText": "patentNumber:(%s)"%patNum, "qf":"applId"}
r = requests.post("https://ped.uspto.gov/api/queries", json=q).json()
try:
    applId = r["queryResults"]["searchResponse"]["response"]["docs"][0]["applId"]
except:
    applId = sys.argv[1]

# Download the file wrapper zip file
print("Downloading File Wrapper for Appl. %s"%applId)

r = requests.get("https://imagefilewrapper.uspto.gov/ifw_images_01/%s/%s/%s/%s.zip"
                    % (str(applId)[0:2], str(applId)[2:5], str(applId)[5:], applId), stream=True)

# Extract the zip file, and merge into one PDF

with zipfile.ZipFile(io.BytesIO(r.content)) as z:

    # Use PyPDF to merge into PDFs
    print("Generating PDF.")
    merger = PyPDF2.PdfFileMerger()

    # Read Metadata from XML
    tree = ET.fromstring(z.read("metadata.xml"))
    documents = tree.findall(".//{urn:us:gov:doc:uspto:common}DocumentBag/{urn:us:gov:doc:uspto:common}Document")

    documentList = []

    for doc in documents:
        DocumentCode = doc.find("{urn:us:gov:doc:uspto:common}DocumentCode").text
        OfficialDocumentDate = doc.find("{urn:us:gov:doc:uspto:common}OfficialDocumentDate").text
        fileName = doc.find("{urn:us:gov:doc:uspto:common}ContentIdentifier").text

        date = datetime.datetime.strptime(OfficialDocumentDate, "%Y-%m-%dT%H:%M:%S%z").strftime("%Y-%m-%d")
        docCode =  docCodes[DocumentCode] if DocumentCode in docCodes else DocumentCode

        docDescription = "%s - %s" % (date, docCode)
        documentList.append((docDescription, fileName))
    
    # Merge into the big PDF
    for docDescription, fileName in documentList:
        print(" - %s"%docDescription)
        merger.append(io.BytesIO(z.read(fileName)), bookmark=docDescription)

    merger.write("FH%s.pdf"%patNum)


