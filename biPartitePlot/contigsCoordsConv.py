import math
import os
import scaffMapPlotter
import crossingMinimization
import sys

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
    #list to contain (contigName, start, range)
    coordContigsDict = {}
    prevEnd = 0
    for (contigName, contigLen) in listContigsRange:
        newStart = prevEnd + 1
        newEnd = math.ceil(float(newStart + (contigLen - 1))\
                               /ContigsConstants.ScaleFactor)
        coordContigsDict[contigName] = (newStart, newEnd, contigLen)
        prevEnd = newEnd
    print contigName, prevEnd
    return coordContigsDict

#return the transformed coordinate map from ref to query
def genCoordsRefQuery(cols, coordContigsDict, contigRefLenIndDict,\
                          contigQueryLenIndDict):

    refContigName = cols[ContigsConstants.RefNameCol]
    refContigId = contigRefLenIndDict[refContigName][1]
    refStart = float(cols[ContigsConstants.RefStartCol])
    refEnd = float(cols[ContigsConstants.RefEndCol])
    refCoord = math.ceil(((refStart + refEnd) / 2)\
                             / ContigsConstants.ScaleFactor)
    refMatchedLen = float(cols[ContigsConstants.RefMatchedLenCol])
    #add to transformed start coordinate of contig
    refTranslatedCoord = coordContigsDict[refContigId][0] + refCoord - 1
    
    queryContigName = cols[ContigsConstants.QueryNameCol]
    queryContigId = contigQueryLenIndDict[queryContigName][1]
    queryStart = float(cols[ContigsConstants.QueryStartCol])
    queryEnd = float(cols[ContigsConstants.QueryEndCol])
    queryCoord = math.ceil(((queryStart + queryEnd) / 2)\
                               / ContigsConstants.ScaleFactor)
    #add to transformed start coordinate of contig, 0 -> start
    queryTranslatedCoord = coordContigsDict[queryContigId][0] + queryCoord - 1

    return (refTranslatedCoord, queryContigId,\
                queryTranslatedCoord, refMatchedLen)


#tranform the mapping from ref to query, in new coords format
def getContigMappedDict(contigMapFilePath, coordContigsDict, minMatchLen,\
                            contigRefLenIndDict,\
                            contigQueryLenIndDict):

    #map to contain 'contigName' -> [(refTranslatedCoord, queryContigName,\
    #            queryTranslatedCoord, refMatchedLen), ...] 
    contigMap = {}

    try:
        contigMapFile = open(contigMapFilePath, 'r')
        header = contigMapFile.readline()
        for line in contigMapFile:
            cols = (line.rstrip('\n')).split()
            coords = genCoordsRefQuery(cols, coordContigsDict,\
                                           contigRefLenIndDict,\
                                           contigQueryLenIndDict)
            if coords[3] < minMatchLen:
                #no need to add as it is less than minimum matched len specified
                continue
            refContigName = cols[ContigsConstants.RefNameCol]
            refContigId = contigRefLenIndDict[refContigName][1]

            if refContigName not in contigMap:
                contigMap[refContigId] = [coords]
            else:
                contigMap[refContigId].append(coords)
        contigMapFile.close()
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)        
    return contigMap


#generate list of forms [('contigName', 'len), ...]
def getContigsDetails(contigsMapFilePath):

    contigRefLenIndDict = {}
    contigQueryLenIndDict = {}
    
    listRefContigsRange = []
    listQueryContigsRange = []
    
    try:
        contigsFile = open(contigsMapFilePath, 'r')
        header = contigsFile.readline()
        refCtr = 0
        queryCtr = 0
        for line in contigsFile:
            cols = (line.rstrip('\n')).split()
            refName = cols[ContigsConstants.RefNameCol]
            if refName not in contigRefLenIndDict:
                contigRefLenIndDict[refName]\
                    = (cols[ContigsConstants.RefLenCol], refCtr)
                refCtr += 1
            queryName = cols[ContigsConstants.QueryNameCol]
            if queryName not in contigQueryLenIndDict:
                contigQueryLenIndDict[queryName]\
                    = (cols[ContigsConstants.QueryLenCol], queryCtr)
                queryCtr += 1
        contigsFile.close()
        for contigName, (contigLen, contigId) in contigRefLenIndDict.iteritems():
            listRefContigsRange.append((contigId, int(contigLen)))
        for contigName,  (contigLen, contigId) in contigQueryLenIndDict.iteritems():
            listQueryContigsRange.append((contigId, int(contigLen)))
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)
    #TODO: return dict to also know how the  contigs were assigned ids
    return (listRefContigsRange, listQueryContigsRange,contigRefLenIndDict,\
                contigQueryLenIndDict)


def parseContigFileNGetMapInfo(contigsMapFilePath, minMatchLen):

    #dictionary to keep contig mapping details
    contigMap = {}

    #get contig details for both sequence
    (listRefContigsRange, listQueryContigsRange,contigRefLenIndDict,\
                contigQueryLenIndDict)\
        = getContigsDetails(contigsMapFilePath)

    print 'Total ref contigs: ', minMatchLen, len(listRefContigsRange)
    print 'Total query contigs: ', minMatchLen, len(listQueryContigsRange)
        
    coordContigRefDict = getConvContigCoordRange(listRefContigsRange)
    coordContigQueryDict = getConvContigCoordRange(listQueryContigsRange)
    
    #combine the coordinate infos from both of above sequence
    coordContigsDict = dict(coordContigRefDict.items()\
                               + coordContigQueryDict.items()) 

    #parse the contig map file to generate the hit maps for each contig
    contigMap = getContigMappedDict(contigsMapFilePath, coordContigsDict,\
                                        minMatchLen, contigRefLenIndDict,\
                                        contigQueryLenIndDict)
    #find total hits
    totalHits = 0
    for contigName, mappingInfos in contigMap.iteritems():
        totalHits += len(mappingInfos)
    print "totalHits: ", minMatchLen, totalHits
    print "Ref contigs hit: ", minMatchLen, len(contigMap) 
    return contigMap


#prepares adjacency list from passed map
def prepareAdjacencyLists(contigMap):
    contigNames = contigMap.keys()
    refAdjacencyList = {}
    queryAdjacencyList = {}
    for refContigName, mappingInfos in contigMap.iteritems():
        for mappingInfo in mappingInfos:
            #mappingInfo[1] contains query scaffold name
            queryContigName = mappingInfo[1]

            if refContigName not in refAdjacencyList:
                refAdjacencyList[refContigName] = [queryContigName]
            else:
                refAdjacencyList[refContigName].append(queryContigName)

            if queryContigName not in queryAdjacencyList:
                queryAdjacencyList[queryContigName] = [refContigName]
            else:
                queryAdjacencyList[queryContigName].append(refContigName)
    return refAdjacencyList, queryAdjacencyList

#plot cross minimized by calling heuristics
def plotCrossMinimizedOrdering(contigMap, minMatchLen = 0):

    refAdjacencyList, queryAdjacencyList = prepareAdjacencyLists(contigMap)
    refList = refAdjacencyList.keys()
    refList.sort()
    queryList = queryAdjacencyList.keys()
    queryList.sort()
    print "plotCross: Num ref contigs: ", minMatchLen, len(refList)
    print "plotCross: Num query contigs: ", minMatchLen,  len(queryList)
    sys.stdout.flush()
    #print refList, queryList
    scaffMapPlotter.plotFromLists(refList,\
                                      queryList,\
                                      refAdjacencyList,\
                                      minMatchLen)
                                      
    refOrderList, queryOrderList =\
        crossingMinimization.minimumCrossingOrdering(refAdjacencyList,\
                                                         queryAdjacencyList)
    #print refOrderList, queryOrderList
    scaffMapPlotter.plotFromLists(refOrderList, queryOrderList,\
                                      refAdjacencyList,\
                                      minMatchLen)

