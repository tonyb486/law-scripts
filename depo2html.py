#!/usr/bin/env python3

import sys,re

if len(sys.argv) != 3:
    print("Usage: %s [ASCII Deposition File] [HTML Output File]"%(sys.argv[0]))
    sys.exit(1)

# We want to limit how much we're actually transforming the transcript,
# and put most of the magic in CSS. Some javascript could be used to
# then allow interactive tweaking of the formatting.
buffer = """
    <style type='text/css'>
        body {  
             width: 500px; margin: 0px auto;
             font-family: georgia;
        } 
        span { 
            display:block;
        }

        span.question {
        }

        span.answer {
        }

        .lineno {
            position: relative;
            left: -80px; top: 0px;
            height:0px; width:0px;
            user-select: none;
        }
    </style>
    """

with open(sys.argv[1], "r") as fd:
    lineClass = ""
    pageNo = 0

    for line in fd.readlines():
        line = line.rstrip().lstrip()

        if not re.match(r"^[0-9]+$", line):
            lineBreak = False

            # Skip unnumbered lines and headers
            if re.match(r"^[0-9]+[ ]*.+", line):
                # Match questions
                if re.match(r"^[0-9]*[ ]*Q[\. ]", line): 
                    line = re.sub(r"^([0-9]*[ ]*)Q[\. ]", r"\1<b>Q.</b>", line)
                    lineClass = "question"
                    buffer += "<br />"

                # Match answers
                elif re.match(r"^[0-9]*[ ]*A[\. ]", line): 
                    line = re.sub(r"^([0-9]*[ ]*)A[\. ]", r"\1<b>A.</b>", line)
                    lineClass = "answer"
                    buffer += "<br />"

                # Match comments/objections/etc
                elif re.match(r"^[0-9]*[ ]*[A-Z][A-Z .]+\:", line):
                    line = re.sub(r"^([0-9]*[ ]*)([A-Z][A-Z .]+\:)", r"\1<b>\2</b>", line)
                    lineClass = "comment"
                    buffer += "<br />"

                # Output the line with some basic HTML formatting
                line = re.sub(r"^([0-9]*)[ ]*(.*)", r"<span class='lineno'>%d:\1</span><span class='line %s'>\2 </span>\n" 
                                                % ( pageNo,  lineClass), line)
                    
                buffer += line

        else: 
            if int(line) == pageNo+1: 
                pageNo += 1

# Output it to a file.
with open(sys.argv[2], "w") as fd:
    fd.write(buffer)

