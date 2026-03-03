#!/usr/bin/env python3
import argparse
import io
import os
import sys
import tempfile
from multiprocessing import Process, Queue, cpu_count

import fitz
from PIL import Image, ImageDraw, ImageFont, features

parser = argparse.ArgumentParser(description="Flatten PDFs into 1-bit image PDFs.")
parser.add_argument("pdfs", metavar="PDFS", nargs="+", type=str, help="PDFs to process")
parser.add_argument(
    "-d", "--dpi", type=int, default=120, help="DPI to render (120 default)"
)
parser.add_argument(
    "-b", "--bates-prefix", type=str, default=False, help="bates prefix to stamp"
)
parser.add_argument(
    "-s",
    "--bates-start",
    type=int,
    default=1,
    help="starting number for bates stamping",
)
parser.add_argument(
    "-c", "--conf-label", type=str, default=False, help="add a confidentialty label"
)
parser.add_argument(
    "-C",
    "--color-jpeg",
    action="store_true",
    help="use color JPEGs instead of B&W TIFFs",
)
parser.add_argument(
    "-t",
    "--threshold",
    type=int,
    default=False,
    help="apply a threshold for monochrome pages (0-255)",
)
parser.add_argument(
    "-D",
    "--no-dither",
    action="store_true",
    help="don't apply floyd-steinberg dithering (useful with threshold)",
)
parser.add_argument(
    "-w",
    "--workers",
    type=int,
    default=cpu_count(),
    help="number of worker threads (default: number of CPUs)",
)
parser.add_argument(
    "--test-page",
    type=int,
    default=False,
    help="process only single page, save as [filename].TEST.pdf",
)
parser.add_argument(
    "--color-pages",
    type=str,
    default=False,
    help="comma-separated list of certain pages to be processed in color",
)

args = parser.parse_args()

if args.color_pages:
    color_pages = [int(i) - 1 for i in args.color_pages.split(",")]
else:
    color_pages = []

dpi = args.dpi
bates_start = args.bates_start

if not args.color_jpeg:
    # Need libtiff as part of Pillow.
    if not features.check_codec("libtiff"):
        print("Pillow compiled without libtiff support. Please reinstall it.")
        print("libtiff is used to provide the image compression used.")
        sys.exit(-1)

# Figure out the font size irrespective of the DPI
fontSize = int(dpi * 0.17)  # (12 points-ish - stupid non-metric))
font = ImageFont.truetype("Arial", fontSize)


# Function to process each page
def process_page(pdf, pageNum, outfile, bs=0):
    # Render the page
    pix = pdf.load_page(pageNum).get_pixmap(dpi=dpi)
    with Image.open(io.BytesIO(pix.tobytes())) as im:
        # Process the page, draw on it as needed
        draw = ImageDraw.Draw(im)

        # Bates stamp, if applicable
        if args.bates_prefix:
            label = "%s%08d" % (args.bates_prefix, bs + pageNum)
            draw.text(
                (im.size[0] - dpi * 0.1, im.size[1] - dpi * 0.1),
                label,
                anchor="rs",
                font=font,
                fill=0,
            )

        # Confidentiality Designation, if applicable
        if args.conf_label:
            draw.text(
                (dpi * 0.1, im.size[1] - dpi * 0.1),
                args.conf_label,
                anchor="ls",
                font=font,
                fill=0,
            )

        # apply a threshold if desired
        if args.threshold and pageNum not in color_pages:
            im = im.point(lambda p: 255 if p > args.threshold else 0)

        with io.BytesIO() as tmp:
            # Compress to TIFF (fax-style Group 4 compression) or JPEG
            if args.color_jpeg or pageNum in color_pages:
                filetype = "jpeg"
                im.save(tmp, format=filetype, dpi=(dpi, dpi))  # Compressed
            else:
                filetype = "tiff"
                # dithering
                if args.no_dither:
                    im = im.convert("1", dither=Image.Dither.NONE)
                else:
                    im = im.convert("1", dither=Image.Dither.FLOYDSTEINBERG)

                im.save(
                    tmp, format=filetype, compression="group4", dpi=(dpi, dpi)
                )  # Compressed

            with fitz.open(stream=tmp, filetype=filetype) as doc:
                fitz.open("pdf", doc.convert_to_pdf()).save(outfile)

        return (pageNum, outfile)


# worker to run the progress
def worker(inqueue, outqueue, tmpdirname):
    cur_pdf = None
    pdf = None
    while True:
        job = inqueue.get()

        # if we're done, we shut down
        if job == "DONE":
            return

        # load the PDF if we haven't yet
        pdff, page, bs = job
        if pdff != cur_pdf:
            pdf = fitz.open(pdff)
            cur_pdf = pdff

        # return the processed file
        outqueue.put(
            process_page(pdf, page, os.path.join(tmpdirname, f"page{page}"), bs)
        )


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Start our worker threads
        inqueue = Queue()
        outqueue = Queue()
        print(f"Starting {args.workers} worker processes...")
        processes = [
            Process(target=worker, args=(inqueue, outqueue, tmpdirname))
            for i in range(args.workers)
        ]
        for p in processes:
            p.start()

        # Process all the PDF files
        for pdff in args.pdfs:
            # Open the PDF file
            pdf = fitz.open(pdff)
            num_pages = pdf.page_count
            # Print progress information
            if args.bates_prefix:
                print(
                    "Rendering '%s' (%d pages) (%s to %s)..."
                    % (
                        pdff,
                        num_pages,
                        "%s%08d" % (args.bates_prefix, bates_start),
                        "%s%08d" % (args.bates_prefix, bates_start + num_pages - 1),
                    )
                )
            else:
                print("Rendering '%s' (%d pages)..." % (pdff, num_pages))

            # Tell the workers to render pixmaps
            for i in range(num_pages):
                inqueue.put((pdff, i, bates_start))

            # Collect the output data from the work queue
            # (list of one-page PDF files)
            pagelist = [outqueue.get() for i in range(num_pages)]

            # Figure out what to call the output file
            if args.test_page:
                filename = f"{pdff}.TEST.pdf"
            elif args.bates_prefix:
                filename = "%s%08d.pdf" % (args.bates_prefix, bates_start)
            else:
                filename = f"{pdff}.FLAT.pdf"

            # Combine the pages back to a single PDF
            print(f"Saving PDF at {filename}...")
            doc = fitz.open()
            for i, file in sorted(pagelist, key=lambda x: x[0]):
                doc.insert_pdf(fitz.open(file))

            doc.save(filename, garbage=4, deflate=True)
            bates_start += num_pages

        # End our worker threads...
        for p in processes:
            inqueue.put("DONE")
        for p in processes:
            p.join()
