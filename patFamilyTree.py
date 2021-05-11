#!/usr/bin/env python3

import requests, json, sys, textwrap, datetime, argparse


try:
   with open("cache.json", "r") as w:
       cache = json.loads(w.read())
except: cache = {}

# Check arguments

parser = argparse.ArgumentParser(description='Generate a Patent Family Tree.')
parser.add_argument('patent', help='the patent number of any patent in the family')

parser.add_argument('--first', action='store_true', default=False,
                    help='include only the latest-filed parent and first child (default: False)')

args = parser.parse_args()

patNum = args.patent

def getApplInfo(patNum=False, applId=False):
    if applId and applId in cache:
        sys.stderr.write("Cache hit on %s!\n"%(applId))
        return cache[applId]

    if patNum:
        q = {"searchText": "patentNumber:(%s)"%patNum, "qf":"applId"}
    elif applId:
        q = {"searchText": "applId:(%s)"%applId, "qf":"applId"}

    r = requests.post("https://ped.uspto.gov/api/queries", json=q).json()
    if r["queryResults"]["searchResponse"]["response"]["numFound"] != 1:
        return []
    
    if applId:
        cache[applId] = r["queryResults"]["searchResponse"]["response"]["docs"][0]

    return r["queryResults"]["searchResponse"]["response"]["docs"][0]
    

seenApps = {}
labels = []
graph = []
years = {}
unknown = False

def processAppl(applId):
    global seenApps, labels, graph, years, unknown

    if applId not in seenApps:
        seenApps[applId] = {"filingDate": "", "children": [] }
        sys.stderr.write("Processing %s\n"%applId)

        appl = getApplInfo(applId=applId)

        if "appStatus_txt" in appl:


            filingDate = datetime.datetime.strptime(appl["appFilingDate"], "%Y-%m-%dT%H:%M:%S%z")
            if filingDate.year in years:
                years[filingDate.year].append(applId)
            else:
                years[filingDate.year] = [applId]

            seenApps[applId] = {"filingDate": filingDate.strftime("%Y-%m-%d"), "children": [] }

            if "patentNumber" in appl:
                labels.append( "\"%s\" [shape=rect, label=< %s >]" % (applId, "<font point-size=\"12\">Pat. %s<br />Appl. %s</font><br /><br /><font point-size=\"10\">%s</font><br />"%("{:,}".format(int(appl["patentNumber"])),applId, "<br />".join(textwrap.wrap(appl["appStatus_txt"],25)))))
            else:
                labels.append( "\"%s\" [shape=rect, style=filled, fillcolor=gray, label=< %s >]" % (applId, "<font point-size=\"12\">Appl. %s</font><br /><br /><font point-size=\"10\">%s</font><br />"%(applId,"<br />".join(textwrap.wrap(appl["appStatus_txt"],25)))))

            if "parentContinuity" in appl:
                parentContinuity = appl["parentContinuity"]
                parentContinuity = sorted(parentContinuity, reverse=True, key=lambda x: datetime.datetime.strptime(x["filingDate"], "%m-%d-%Y").strftime("%Y-%m-%d"))

                for n,i in enumerate(parentContinuity):
                    processAppl(applId=i["claimApplicationNumberText"])

                    if n == 0 or not args.first:
                        graph.append("\"%s\" -> \"%s\" [penwidth=.5] "%(i["claimApplicationNumberText"], applId))
            
            if "childContinuity" in appl:                
                childContinuity = appl["childContinuity"]
                childContinuity = sorted(childContinuity, reverse=False, key=lambda x: datetime.datetime.strptime(x["filingDate"], "%m-%d-%Y").strftime("%Y-%m-%d"))
                seenApps[applId]["children"] = [i["claimApplicationNumberText"] for i in childContinuity]

                for n,i in enumerate(childContinuity):
                    processAppl(applId=i["claimApplicationNumberText"])

                    if n == 0 or not args.first:
                        graph.append("\"%s\" -> \"%s\" [penwidth=.5] "%(applId, i["claimApplicationNumberText"]))

        else:
            unknown = True
            # This is sloppy.
            labels.append( "\"%s\" [shape=rect, style=filled, fillcolor=orange, label=< %s >]" % (applId, "<font point-size=\"12\">Appl. %s</font><br /><br /><font point-size=\"10\">%s</font><br />"%(applId,"(Unpublished/Unknown)")))
            
            parentApps = []
            for i in seenApps.keys():
                if applId in seenApps[i]["children"]:
                    parentApps.append((i, seenApps[i]["filingDate"]))
            
            parentApps = sorted(parentApps, reverse=True, key=lambda x: x[1])
            if len(parentApps)>0:
                graph.append("\"%s\" -> \"%s\" [penwidth=.5] "%(parentApps[0][0], applId))
                sys.stderr.write("Unpublished: %s [Parents: %s]\n"%(applId, json.dumps(parentApps)))

            # Warning: Year 99999 bug! (lol)
            if "99999" in years:
                years[99999].append(applId)
            else:
                years[99999] = [applId]


print("strict digraph G {")
startApp = getApplInfo(patNum=patNum)
processAppl(startApp["applId"])

# Set up the year nodes
print("graph [nodesep=1]")
print("node [fontsize=24, shape = plaintext];")
if unknown: print("{99999 [label=\"Unknown\"]}")

yearList = sorted(list(years.keys()))
for f,s in zip(yearList, yearList[1:]):
    print("%d -> %d"%(f,s))

# Set up the labels
print("{%s}"%("\n".join(labels)))

# Rank everything together
for yr in yearList:
    print("{rank=same; %s %s }"%(yr, " ".join("\"%s\""%i for i in years[yr])))

# Print the graph
print("\n".join(graph))

print("}")



with open("cache.json", "w") as w:
    w.write(json.dumps(cache))
