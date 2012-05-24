import math
import os

"""convert contigs mapping to contigs coordinates
which can eventually be plotted"""
class ContigsConstants:
    
    #factor specifying how many bases forms a dot
    ScaleFactor = 1

    #columns specifying start and end positions of matching regions of ref
    RefStartCol = 1 - 1
    RefEndCol = 2 - 1
    
    #column specifying reference length
    RefLenCol = 8 - 1

    #column specifying ref name
    RefNameCol =  12 - 1

    #refMatchedLen col
    RefMatchedLenCol = 5 - 1
    
    #column specifying query length
    QueryLenCol = 9 - 1 

    #column specifying query name
    QueryNameCol = 13 - 1
    
    #columns specifying start and end positions of matching regions of query
    QueryStartCol = 3 - 1
    QueryEndCol = 4 - 1

    #queryMatchedLenCol
    queryMatchedLenCol = 6 - 1


#passed list in format ('contigName', 'len)
#return a dict in format contigName -> (start, end, len)
def getConvContigCoordRange(listContigsRange):
    #TODO may need to sort in specific order
    #list to contain (scaffName, start, range)
    coordContigsDict = {}
    prevEnd = 0
    for (contigName, len) in listContigsRange:
        newStart = prevEnd + 1
        newEnd = math.ceil(float(newStart + (len - 1))\
                               /ContigsConstants.ScaleFactor)
        coordContigsDict[contigName] = (newStart, newEnd, len)
        prevEnd = newEnd
    print contigName, prevEnd
    return coordContigsDict

#return the transformed coordinate map from ref to query
def genCoordsRefQuery(cols, coordContigsDict):

    refContigName = cols[ContigsConstants.RefNameCol]
    refStart = float(cols[ContigsConstants.RefStartCol])
    refEnd = float(cols[ContigsConstants.RefEndCol])
    refCoord = math.ceil(((refStart + refEnd) / 2)\
                             / ContigsConstants.ScaleFactor)
    refMatchedLen = float(cols[ContigsConstants.RefMatchedLenCol])
    #add to transformed start coordinate of contig
    refTranslatedCoord = coordContigsDict[refContigName][0] + refCoord - 1
    
    queryContigName = getQueryContigName(cols[ContigsConstants.QueryNameCol])
    queryStart = float(cols[ContigsConstants.QueryStartCol])
    queryEnd = float(cols[ContigsConstants.QueryEndCol])
    queryCoord = math.ceil(((queryStart + queryEnd) / 2)\
                               / ContigsConstants.ScaleFactor)
    #add to transformed start coordinate of contig, 0 -> start
    queryTranslatedCoord = coordContigsDict[queryContigName][0] + queryCoord - 1

    return (refTranslatedCoord, queryContigName,\
                queryTranslatedCoord, refMatchedLen)


#tranform the mapping from ref to query, in new coords format
def getContigMappedDict(contigMapFilePath, coordContigsDict):

    #map to contain 'contigName' -> [(refTranslatedCoord, queryContigName,\
    #            queryTranslatedCoord, refMatchedLen), ...] 
    contigMap = {}

    try:
        contigMapFile = open(contigMapFilePath, 'r')
        header = contigMapFile.readline()
        for line in contigMapFile:
            cols = (line.rstrip('\n')).split()
            coords = genCoordsRefQuery(cols, coordContigsDict)
            refContigName = cols[ContigsConstants.RefNameCol]
            if refContigName not in contigMap:
                contigMap[refContigName] = [coords]
            else:
                contigMap[refContigName].append(coords)
        contigMapFile.close()
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)        
    return contigMap

def getQueryContigName(contigName):
    return contigName.split('|')[3]

#generate list of forms [('contigName', 'len), ...]
def getContigsDetails(contigsMapFilePath):

    contigRefLenDict = {}
    contigQueryLenDict = {}
    listRefContigsRange = []
    listQueryContigsRange = []
    try:
        contigsFile = open(contigsMapFilePath, 'r')
        header = contigsFile.readline()
        for line in contigsFile:
            cols = (line.rstrip('\n')).split()
            contigRefLenDict[cols[ContigsConstants.RefNameCol]]\
                = cols[ContigsConstants.RefLenCol]
            queryContigName = getQueryContigName(\
                cols[ContigsConstants.QueryNameCol])
            contigQueryLenDict[queryContigName]\
                = cols[ContigsConstants.QueryLenCol]
        contigsFile.close()
        for contigName, contigLen in contigRefLenDict.iteritems():
            listRefContigsRange.append((contigName, int(contigLen)))
        for contigName, contigLen in contigQueryLenDict.iteritems():
            listQueryContigsRange.append((contigName, int(contigLen)))
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)
    return (listRefContigsRange, listQueryContigsRange)


def parseContigFileNGetMapInfo(contigsMapFilePath):

    #dictionary to keep contig mapping details
    contigMap = {}

    #get contig details for both sequence
    (listRefContigsRange, listQueryContigsRange)\
        = getContigsDetails(contigsMapFilePath)
    
    coordContigRefDict = getConvContigCoordRange(listRefContigsRange)
    coordContigQueryDict = getConvContigCoordRange(listQueryContigsRange)
    
    #combine the coordinate infos from both of above sequence
    coordContigsDict = dict(coordContigRefDict.items()\
                               + coordContigQueryDict.items()) 

    #parse the contig map file to generate the hit maps for each contig
    contigMap = getContigMappedDict(contigsMapFilePath, coordContigsDict)
    return contigMap
        
