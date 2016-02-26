import re
import synapseclient

_headers = dict(team="## **Team Name**", datasets="## **Identification of Datasets Used**",
                methods="## **Methods**", collaboration="## **Collaboration**",
                narrative="## **Project Narrative**", code="## **Code**")

_headers_re = dict(team="^## \*\*Team Name\*\*", 
                   datasets="^## \*\*Identification of Datasets Used\*\*",
                   methods="^## \*\*Methods\*\*", 
                   collaboration="^## \*\*Collaboration\*\*",
                   narrative="^## *\*\*Project Narrative\*\*", 
                   code="^## *\*\*Code\*\*")


_headers_order = ["team", "datasets", "methods", "narrative", "collaboration", "code"]

_maxNarrativeLength = 24000
_maxMethodsLength = 16000
_maxDatasetsLength = 4000

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
    wl = filter(lambda x: len(x) > 0 and (not x.startswith("${")) and (x.find("|") < 0) and (not x.startswith("> This is a sample project")), wl)
    return wl

def findHeaderPos(wl):
    posDict = {}

    for (n, x) in enumerate(wl):

        for k, v in _headers.iteritems():
            if (x.find(v) >= 0):
                posDict[k] = n

    return posDict

def findHeaderPosRe(wl):
    posDict = {}

    for (n, x) in enumerate(wl):

        for k, v in _headers_re.iteritems():
            pos = re.findall(v, x)
            if (len(pos) > 0):
                posDict[k] = n

    return posDict
   

def removeCodeBlocks(wl):
    """Remove code blocks (delimited by '```').
    
    """
    
    idxs = []
    toremove = []

    for (n, x) in enumerate(wl):

        if (x == "```"):

            idxs += [n]

            if (len(idxs) == 2):
                toremove += range(idxs[0], idxs[1] + 1)
                idxs = []

    wl[:] = [x for (n, x) in enumerate(wl) if n not in toremove]

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
    tmp = map(lambda x: re.sub("\${.*?inlineWidget.*?}", "", x), tmp)
    
    return tmp

def validate_header_order(wmarkdown):
    wl = cleanWiki(wmarkdown)
    posDict = findHeaderPosRe(wl)
    
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
    """Check for the existence of the headers.

    """

    wl = cleanWiki(wmarkdown)

    # wl[:] = removeCodeBlocks(wl)

    # Find the lines of methods, narrative and collab headers
    posDict = findHeaderPosRe(wl)

    errors = []

    for k in _headers.keys():
        if k not in posDict.keys():
            errors += ["Missing %s header." % (k,)]

    if len(errors) > 0:
        return False, "\n".join(errors)
    else:
        return True, "Headers validated."

def validate_wordcounts(wmarkdown):
    """Check the datasets, methods and narrative sections to see if word count limits are met.

    """

    wl = cleanWiki(wmarkdown)

    wl[:] = removeCodeBlocks(wl)

    # Find the lines of methods, narrative and collab headers
    posDict = findHeaderPos(wl)

    # Datasets should in between the datasets and method headers
    datasets = wl[posDict['datasets'] + 1:posDict['methods']]
    datasets = cleanSections(datasets)
    datasetsLength = sum(map(len, datasets))

    # Methods should in between the method and narrative headers
    methods = wl[posDict['methods'] + 1:posDict['narrative']]
    methods = cleanSections(methods)
    methodsLength = sum(map(len, methods))

    # Narrative should be between the narrative and collab headers
    narrative = wl[posDict['narrative'] + 1:posDict['collaboration']]
    narrative = cleanSections(narrative)
    narrativeLength = sum(map(len, narrative))

    errors = []
    if datasetsLength > _maxDatasetsLength:
        errors += ["Dataset identification section is too long (%s characters). Maximum is %s." % (datasetsLength, _maxDatasetsLength)]

    if methodsLength > _maxMethodsLength:
        errors += ["Methods section is too long (%s characters). Maximum is %s." % (methodsLength, _maxMethodsLength)]

    if narrativeLength > _maxNarrativeLength:
        errors += ["Narrative section is too long (%s characters). Maximum is %s." % (narrativeLength, _maxNarrativeLength)]

    if len(errors) > 0:
        return False, "\n".join(errors)
    else:
        return True, "Word count validated (datasets: %s characters, methods: %s characters, narrative section: %s characters)." % (datasetsLength, methodsLength, narrativeLength)

def validate_abstract(projectId, syn):
    abstractId = findAbstract(projectId,  syn)

    if abstractId:

        try:
            w = syn.getWiki(abstractId)
        except synapseclient.exceptions.SynapseHTTPError as e:
            return (False, "Found abstract folder at %s, but a Wiki has not been added to it. Please add the text of your abstract to the Wiki of that Folder." % (abstractId, ))

        wMarkdown = w['markdown']

        wl = cleanWiki(wMarkdown)
        wl[:] = removeCodeBlocks(wl)
        abstractLength = sum(map(len, wl))

        if abstractLength > 0:
            return (True, "Found non-empty abstract at %s (%s characters)" % (abstractId, abstractLength))
        else:
            return (False, "Found abstract folder at %s but no text. Please add the text of your abstract to the Wiki of that Folder." % (abstractId, ))
    else:
        return (False, "No abstract found. Please add an Abstract Folder and put the text of your abstract on the Wiki of that Folder. If you have created an Abstract Folder, please check the Sharing settings.")

def validate_panel_access(projectId, syn):
    
    try:
        perms = syn.getPermissions(projectId, _evalPanelId)
    except synapseclient.exceptions.SynapseHTTPError as e:
        return (False, "Evaluation panel cannot read the project.")

    if perms == [u'READ']:
        return (True, "Evaluation panel can read the project.")
    elif u'READ' in perms and len(perms) > 1:
        return (False, "Evaluation panel can do more than read. Only provide read permissions.")
    else:
        return (False, "Evaluation panel cannot read the project.")
