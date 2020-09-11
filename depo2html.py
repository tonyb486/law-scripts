#!/usr/bin/env python3

import sys,re

if len(sys.argv) != 3:
    print("Usage: %s [ASCII Deposition File] [HTML Output File]"%(sys.argv[0]))
    sys.exit(1)

# We want to limit how much we're actually transforming the transcript,
# and put most of the magic in CSS. Some simple javascript is used to
# then allow interactive tweaking of the formatting.
buffer = """
<head>
    <style type='text/css'>
        body {  
             width: 500px; margin: 0px auto;
             font-family: georgia;
             fontSize: 16px;
        } 

        span { 
            display:block;
        }

        .inline {
            display: inline;
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
        
        .hidden {
            display: none
        }


        #controls {
            font-size: 12px;
            font-family: sans-serif;
            position: fixed;
            background: #eee;
            border: 2px solid #ccc;
            width: 150px;
            padding: 10px;
            top: 10px;
            right: 20px;
            opacity: .5;
        }
        div.break {
            margin: 12px;
        }
    </style>

    <script type="text/javascript">

        function toggleClass(selector, className) {
            var elems = document.querySelectorAll(selector);
            elems.forEach(i => i.classList.toggle(className));
        }

        function changeFontSize(direction) {
            var body = document.querySelector('div#body');
            curFontSize = parseInt(body.style.fontSize)
            if (Number.isNaN(curFontSize)) curFontSize = 16
            if(direction == "up")  body.style.fontSize = curFontSize+4
            if(direction == "down")  body.style.fontSize = curFontSize-4
        }

    </script>

</head>

<div id="controls">
    <div id="innerControls">
        <div style="text-align: center; font-weight: bold">Controls</div>
        <br />
        <input type="checkbox" onchange="toggleClass('.lineno', 'hidden')" checked>Show Line Numbers</input>
        <br />
        <input type="checkbox" onchange="toggleClass('.line', 'inline')" checked>Match transcript lines</input>
        <hr />
        Font Size:
        <input type="button" onclick="changeFontSize('up')" value="+">
        <input type="button" onclick="changeFontSize('down')" value="-">
        <hr />
    </div>
    <div style="text-align: center">
        <input type="button" onclick="toggleClass('#innercontrols', 'hidden')" value="Toggle Controls">
    </div>

</div>
<div id="body">
    """

with open(sys.argv[1], "r") as fd:
    lineClass = ""
    pageNo = 0

    for line in fd.readlines():
        line = line.rstrip().lstrip().encode("ascii", errors="ignore").decode()

        if not re.match(r"^[0-9]+$", line):
            lineBreak = False

            # Skip unnumbered lines and headers
            if re.match(r"^[0-9]+[ ]*.+", line):
                # Match questions
                if re.match(r"^[0-9]*[ ]*Q[\. ]", line): 
                    line = re.sub(r"^([0-9]*[ ]*)Q[\. ]", r"\1<b>Q.</b>", line)
                    lineClass = "question"
                    buffer += "<div class='break'></div>"

                # Match answers
                elif re.match(r"^[0-9]*[ ]*A[\. ]", line): 
                    line = re.sub(r"^([0-9]*[ ]*)A[\. ]", r"\1<b>A.</b>", line)
                    lineClass = "answer"
                    buffer += "<div class='break'></div>"

                # Match comments/objections/etc
                elif re.match(r"^[0-9]*[ ]*[A-Z][A-Z .]+\:", line):
                    line = re.sub(r"^([0-9]*[ ]*)([A-Z][A-Z .]+\:)", r"\1<b>\2</b>", line)
                    lineClass = "comment"
                    buffer += "<div class='break'></div>"

                # Output the line with some basic HTML formatting
                line = re.sub(r"^([0-9]*)[ ]*(.*)", r"<span class='lineno'>%d:\1</span><span class='line %s'>\2 </span>\n" 
                                                % ( pageNo,  lineClass), line)
                    
                buffer += line

        else: 
            if int(line) == pageNo+1: 
                pageNo += 1

buffer += "</div>"

# Output it to a file.
with open(sys.argv[2], "w") as fd:
    fd.write(buffer)

