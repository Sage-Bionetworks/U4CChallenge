_headers = dict(methods="**Methods**", collab="**Collaboration**",
                narrative="**Project Narrative**")

_headers_order = ["methods", "narrative", "collab"]

_maxNarrativeLength = 24000
_maxMethodsLength = 16000

def cleanWiki(w):
    wl = w.split("\n")
    wl = filter(lambda x: len(x) > 0 and (not x.startswith("${")) and (not x.startswith("> This is a sample project")), wl)
    return wl

def findHeaderPos(wl):
    posDict = {}

    for (n, x) in enumerate(wl):

        for k, v in _headers.iteritems():
            if (x.find(v) > 0):
                posDict[k] = n

    return posDict

def removeCodeBlocks(wl):
    idxs = []
    toremove = []

    for (n, x) in enumerate(wl):

        if (x == "```"):

            idxs += [n]

            if (len(idxs) == 2):
                toremove += range(idxs[0], idxs[1] + 1)
                idxs = []
                found = 0

    for x in toremove:
        wl.pop(x)

    return wl

def cleanSections(sectionList):
    """Clean up an individual section (list of text lines).

    Remove headers with sub-depth at least 3, markdown-style links ( [foo](bar) ),
    and Synapse IDs.

    """

    tmp = list(sectionList)
    tmp = filter(lambda x: not x.startswith("###"),  tmp)
    tmp = map(lambda x: re.sub(" \[(.*?)\]\(.*?\) ", " \\1 ", x), tmp)
    tmp = map(lambda x: re.sub("syn\d+", "", x), tmp)
    return tmp

def validate_header_order(wmarkdown):
    wl = cleanWiki(wmarkdown)
    posDict = findHeaderPos(wl)

    errors = []

    for n, x in enumerate(_headers_order[1:]):
        if posDict[_headers_order[x - 1]] < posDict[_headers_order[x]]:
            errors += ["Header %s out of order." % (_headers_order[x - 1],)]

    if len(errors) > 0:
        return False, "\n".join(errors)
    else:
        return True, "Header order validated."

def validate_headers(wmarkdown):
    """Find the methods, narrative, and collaborator headers.

    """

    wl = cleanWiki(wmarkdown)

    wl[:] = removeCodeBlocks(wl)

    # Find the lines of methods, narrative and collab headers
    posDict = findHeaderPos(wl)

    errors = []

    for k in _header.keys():
        if k not in posDict.keys():
            errors += ["Missing %s header." % (k,)]

    if len(errors) > 0:
        return False, "\n".join(errors)
    else:
        return True, "Headers validated."

def validate_wordcounts(wmarkdown):
    """Check the methods and narrative sections to see if word count limits are met.

    """

    wl = cleanWiki(wmarkdown)

    wl[:] = removeCodeBlocks(wl)

    # Find the lines of methods, narrative and collab headers
    posDict = findHeaderPos(wl)

    # Methods should in between the method and narrative headers
    methods = wl[posDict['methods'] + 1:posDict['narrative']]
    methods = cleanSections(methods)
    methodsLength = sum(map(len, methods))

    # Narrative should be between the narrative and collab headers
    narrative = wl[posDict['narrative'] + 1:posDict['collab']]
    narrative = cleanSections(narrative)
    narrativeLength = sum(map(len, narrative))

    errors = []

    if methodsLength > _maxMethodsLength:
        errors += ["Methods section is too long (%s characters). Maximum is %s." % (methodsLength, )]

    if narrativeLength > _maxNarrativeLength:
        errors += ["Narrative section is too long (%s characters)." % (narrativeLength, )]

    if len(errors) > 0:
        return False, "\n".join(errors)
    else:
        return True, "Word count validated."
