import re

_headers = dict(methods="**Methods**", collab="**Collaboration**",
                narrative="**Project Narrative**")

_headers_order = ["methods", "narrative", "collab"]

_maxNarrativeLength = 24000
_maxMethodsLength = 16000

_evalPanelId = 3331171

def findAbstract(parentId, syn):
    r = syn.query('select id,name from folder where parentId=="%s"' % (parentId, ))
    r = filter(lambda x: x['folder.name'] == "Abstract", r['results'])

    if len(r) > 0:
        return r[0]['folder.id']
    else:
        return None

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

    for x in range(1, len(_headers_order)):
        header1, header2 = _headers_order[x-1], _headers_order[x]

        if posDict[header1] > posDict[header2]:
            errors += ["Header %s out of order." % (header1, )]

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

    for k in _headers.keys():
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
        return True, "Word count validated. Methods section: %s, Narrative section: %s" % (methodsLength, narrativeLength)

def validate_abstract(projectId, syn):
    abstractId = findAbstract(projectId,  syn)

    w = syn.getWiki(abstractId)
    wMarkdown = w['markdown']

    if abstractId:
        if len(wMarkdown) > 0:
            return (True, "Found non-empty abstract at %s" % (abstractId, ))
        else:
            return (False, "Found abstract at %s, but no text." % (abstractId, ))
    else:
        return (False, "No abstract found")

def validate_panel_access(projectId, syn):

    perms = syn.getPermissions('syn4154450', _evalPanelId)

    if perms == [u'READ']:
        return (True, "Evaluation panel can read the project.")
    elif u'READ' in perms and len(perms) > 1:
        return (False, "Evaluation panel can do more than read. Only provide read permissions.")
    else:
        return (False, "Evaluation cannot read the project.")
