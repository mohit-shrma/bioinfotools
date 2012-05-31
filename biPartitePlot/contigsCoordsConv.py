import math
import os
import scaffMapPlotter
import crossingMinimization
import sys

"""convert contigs mapping to contigs coordinates
which can eventually be plotted"""
class ContigsConstants:
    
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
#return a list in format  [(start, end, len), ...]
def getConvContigCoordRange(listContigsRange):
    coordContigsRange = []
    prevEnd = 0
    for (contigName, contigLen) in listContigsRange:
        newStart = prevEnd + 1
        newEnd = math.ceil(float(newStart + (contigLen - 1))\
                               /ContigsConstants.ScaleFactor)
        coordContigsRange.append((newStart, newEnd, contigLen))
        prevEnd = newEnd
    print listContigsRange[-1][0], prevEnd
    return coordContigsRange

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



#optimized getContigsDetails version
def getContigsDetails(contigsMapFilePath, minMatchLen):

    contigRefLenIndDict = {}
    contigQueryLenIndDict = {}
    
    
    #contains reference [(name, len), ...]
    refContigsNameLen = []

    #contains query [(name, len), ...]
    queryContigsNameLen = []

    #contains details of query hitting ref, just the indices of query
    # [[q1,q2], ...]
    refAdjList = []

    #contains details of ref hitting query, just the indices of ref
    # [[r1,r2], ...]
    queryAdjList = []

    
    try:
        contigsFile = open(contigsMapFilePath, 'r')
        header = contigsFile.readline()
        for line in contigsFile:

            cols = (line.rstrip('\n')).split()

            refMatchedLen = float(cols[ContigsConstants.RefMatchedLenCol])

            #only consider matches satisfying minimum matching length passed
            if refMatchedLen < minMatchLen:
                continue
            
            refName = cols[ContigsConstants.RefNameCol]
            if refName not in contigRefLenIndDict:
                contigRefLenIndDict[refName]\
                    = (cols[ContigsConstants.RefLenCol], refCtr)
                refContigsNameLen.append((refName,\
                                              cols[ContigsConstants.RefLenCol]))
                refCtr += 1

            queryName = cols[ContigsConstants.QueryNameCol]
            if queryName not in contigQueryLenIndDict:
                contigQueryLenIndDict[queryName]\
                    = (cols[ContigsConstants.QueryLenCol], queryCtr)
                queryContigsNameLen.append(queryName,\
                                               cols[ContigsConstants.QueryLenCol])
                queryCtr += 1

            refInd = contigRefLenIndDict[refName][1]
            queryInd = contigQueryLenIndDict[queryName][1]

            #if size of adjlist is gr8r or equal to current ref indices than
            #directly add to adjacency list
            if len(refAdjList) >= refInd + 1:
                refAdjList[refInd].append(queryInd)
            elif len(refAdjList) == refInd:
                #not present in adj list, new entry
                refAdjList[refInd] = [queryInd]
            else:
                print 'error adding to reference adjacency list'

            #add to query adjacency list similar as above
            if len(queryAdjList) >= queryInd + 1:
                queryAdjList[queryInd].append(refInd)
            elif len(queryAdjList) == queryInd:
                #not present in adj list, new entry
                queryAdjList[queryInd] = [refInd]
            else:
                print 'error adding to query adjacency list'
            
        contigsFile.close()
            
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)
    return refContigsNameLen, queryContigsNameLen, refAdjList, queryAdjList



def parseContigFileNGetMapInfo(contigsMapFilePath, minMatchLen):

    #dictionary to keep contig mapping details
    contigMap = {}

    #get contig details for both sequence
    refContigsNameLen, queryContigsNameLen, refAdjList, queryAdjList =\
        getContigsDetails(contigsMapFilePath, minMatchLen)

    print 'ref contigs hit: ', len(refContigsNameLen)
    print 'query contigs hit: ', len(queryContigsNameLen)
        
    #find total hits
    totalHits = sum([len(queryHits) for queryHits in refAdjList])
    print "totalHits/lines: ", minMatchLen, totalHits
    return refContigsNameLen, queryContigsNameLen, refAdjList, queryAdjList


#plot cross minimized by calling heuristics
def plotCrossMinimizedOrdering(refAdjList, queryAdjList, minMatchLen = 0):

    refList = refAdjList.keys()
    refList.sort()
    queryList = queryAdjList.keys()
    queryList.sort()
    sys.stdout.flush()
    #print refList, queryList
    scaffMapPlotter.plotFromArrayAdjList(refAdjList,\
                                      queryAdjList,\
                                      minMatchLen)

    #TODO: as per new adjacency format modify cross minimization file
    refOrderList, queryOrderList =\
        crossingMinimization.minimumCrossingOrdering(refAdjacencyList,\
                                                         queryAdjacencyList)
    #print refOrderList, queryOrderList
    scaffMapPlotter.plotFromLists(refOrderList, queryOrderList,\
                                      refAdjacencyList,\
                                      minMatchLen)

