#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont, features
import sys, fitz, io, argparse, random
from tqdm import tqdm

def main():

    parser = argparse.ArgumentParser(description="Flatten PDFs into 1-bit image PDFs.")
    parser.add_argument('pdfs', metavar='PDFS', nargs='+', type=str, help="PDFs to process")
    parser.add_argument('-d', '--dpi', type=int, default=120, help="DPI to render (120 default)")
    parser.add_argument('-b', '--bates-prefix', type=str, default=False, help="bates prefix to stamp")
    parser.add_argument('-s', '--bates-start', type=int, default=1, help="starting number for bates stamping")
    parser.add_argument('-c', '--conf-label', type=str, default=False, help="add a confidentialty label")
    parser.add_argument('-r', '--rand-skew', action='store_true', help="rotate each page slightly to look scanned")
    parser.add_argument('--skew-max', type=int, default=10, help="max amount to rotate if (in 10ths of a degree) (10 default)")

    args = parser.parse_args()

    dpi = args.dpi
    bates_start = args.bates_start

    # Need libtiff as part of Pillow.
    if not features.check_codec("libtiff"):
        print("Pillow compiled without libtiff support. Please reinstall it.")
        print("libtiff is used to provide the image compression used.")
        sys.exit(-1)

    # Figure out the font size irrespective of the DPI
    fontSize = int(dpi * 0.17) # (12 points-ish - stupid non-metric))
    font = ImageFont.truetype("Arial", fontSize)

    # Function to process each page
    def process_page(page,bs=0):

        # Render the page
        pix = page.get_pixmap(dpi=dpi)  
        with Image.open(io.BytesIO(pix.tobytes())) as im:

            # Since this is a popular thing apparently, just for fun
            if args.rand_skew:
                im = im.rotate(random.randrange(-args.skew_max,args.skew_max)*0.1, 
                              expand=False, resample=Image.BILINEAR,
                              fillcolor=(5,5,5))

            # Process the page, draw on it as needed
            draw = ImageDraw.Draw(im)

            # Bates stamp, if applicable
            if args.bates_prefix:
                label = "%s%08d"%(args.bates_prefix,bs+page.number) 
                draw.text((im.size[0]-dpi*.1,im.size[1]-dpi*.1), label, 
                        anchor="rs", font=font, fill=0)
            
            # Confidentiality Designation, if applicable
            if args.conf_label:
                draw.text((dpi*.1,im.size[1]-dpi*.1), args.conf_label, 
                    anchor="ls", font=font, fill=0)

            # Compress to TIFF (fax-style Group 4 compression) and back
            with io.BytesIO() as tmp:
                im = im.convert("1") # Monochrome
                im.save(tmp,format="tiff",compression="group4", dpi=(dpi,dpi)) # Compressed

                # Convert this to a PDF object with PyMuPDF again
                with fitz.open(stream=tmp, filetype="tiff") as doc:
                    stream = doc.convert_to_pdf()
                    return fitz.open("pdf", stream)

    # Process all the PDF files
    for i in args.pdfs:

        # Open the PDF file
        pdf = fitz.open(i)  

        # Print progress information
        print("Processing '%s' (%d pages)"%(i,pdf.page_count))
        if args.bates_prefix:
            print("Bates stamping from %s to %s"%("%s%08d"%(args.bates_prefix,bates_start),
                                                 "%s%08d"%(args.bates_prefix,bates_start+pdf.page_count-1)))

        # Create the output file, and append to it the pages created
        # by converting the rendered pixmaps to TIFF and then back into fitz
        doc = fitz.open()
        for page in tqdm(pdf, total=pdf.page_count):
            with process_page(page,bates_start) as ipage:
                doc.insert_pdf(ipage)

        # Save the file
        if args.bates_prefix:
            doc.save("%s%08d.pdf"%(args.bates_prefix,bates_start),garbage=4,deflate=True)
        else:
            doc.save(i+".FLAT.pdf",garbage=4,deflate=True)
        
        bates_start += pdf.page_count

if __name__ == "__main__":
    main()
