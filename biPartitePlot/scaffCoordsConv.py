import math
import os
import scaffMapPlotter
import crossingMinimization

"""convert scaffold mapping to another scaffold coordinates mapping which can
eventually be plotted """
class MyError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

#class to hold some constants, which won't be change while executing
class ScaffConstants:

    #MAX_ITERATION_COUNTER
    MAX_ITERATION_COUNTER = 50
    
    #factor specifying how many bases forms a dot
    ScaleFactor = 1

    #columns specifying start and end positions of matching regions of ref
    RefStartCol = 4#2#5 - 1
    RefEndCol = 5#3#6 - 1
    
    #column specifying reference length
    RefLenCol = 3#1#4 - 1

    #column specifying ref name
    RefNameCol =  1#0#2 - 1
    
    #column specifying query length
    QueryLenCol = 8#7#9 - 1 

    #column specifying query name
    QueryNamecol = 6#4#7 - 1
    
    #columns specifying start and end positions of matching regions of query
    QueryStartCol = 9#5#10 - 1
    QueryEndCol = 10#6#11 - 1

    #stats file scaff name
    StatsNameCol = 1 - 1

    #stats file scaff length
    StatsLengthCol = 2 - 1

#passed list in format ('scaffName', 'len)
#return a dict in format scaffName -> (start, end, len)
def getConvScaffCoordRange(listScaffsRange):
    #list to contain (scaffName, start, range)
    coordScaffsDict = {}
    prevEnd = 0
    for (scaffName, length) in listScaffsRange:
        newStart = prevEnd + 1
        newEnd = math.ceil(float(newStart + (length - 1))\
                               /ScaffConstants.ScaleFactor)
        coordScaffsDict[scaffName] = (newStart, newEnd, length)
        prevEnd = newEnd
    print scaffName, prevEnd
    return coordScaffsDict


#return the transformed coordinate map from ref to query
def genCoordsRefQuery(cols, coordScaffsDict):

    refScaffName = cols[ScaffConstants.RefNameCol]
    refStart = float(cols[ScaffConstants.RefStartCol])
    refEnd = float(cols[ScaffConstants.RefEndCol])
    refCoord = math.ceil(((refStart + refEnd) / 2) / ScaffConstants.ScaleFactor)
    #TODO: check whether -1 needs to be added
    refMatchedLen = refEnd - refStart
    #add to transformed start coordinate of scaffold
    refTranslatedCoord = coordScaffsDict[refScaffName][0] + refCoord - 1
    
    queryScaffName = cols[ScaffConstants.QueryNamecol]
    queryStart = float(cols[ScaffConstants.QueryStartCol])
    queryEnd = float(cols[ScaffConstants.QueryEndCol])
    queryCoord = math.ceil(((queryStart + queryEnd) / 2)\
                               / ScaffConstants.ScaleFactor)
    #add to transformed start coordinate of scaffold, 0 -> start
    queryTranslatedCoord = coordScaffsDict[queryScaffName][0] + queryCoord - 1

    return (refTranslatedCoord, queryScaffName,\
                queryTranslatedCoord, refMatchedLen)
    

#tranform the mapping from ref to query, in new coords format
def getScaffMappedList(scaffMapFilePath, coordScaffsDict, minMatchedLen = 5000):
    mappingInfos = []
    refScaffName = ''
    try:
        scaffMapFile = open(scaffMapFilePath, 'r')
        header = scaffMapFile.readline()
        for line in scaffMapFile:
            cols = (line.rstrip('\n')).split()
            coords = genCoordsRefQuery(cols, coordScaffsDict)
            if coords[3] < minMatchedLen:
                #no need to add as it is less than minimum matched len specified
                continue
            if not refScaffName:
                refScaffName = cols[ScaffConstants.RefNameCol]
            mappingInfos.append(coords)
        scaffMapFile.close()
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)        
    return (refScaffName, mappingInfos)


#generate list of forms [('scaffName', 'len), ...]
def getScaffsDetails(scaffsFilePath):
    listScaffsRange = []
    try:
        scaffsFile = open(scaffsFilePath, 'r')
        header = scaffsFile.readline()
        for line in scaffsFile:
            cols = (line.rstrip('\n')).split()
            scaffName = cols[ScaffConstants.StatsNameCol]
            scaffLen = float(cols[ScaffConstants.StatsLengthCol])
            if scaffLen:
                listScaffsRange.append((scaffName, scaffLen))
        scaffsFile.close()
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)
    return listScaffsRange

def parseScaffDirNGetMapInfo(scaffDir, scaffsFile1Path, scaffsFile2Path,\
                                 minMatchLen):

    #dictionary to keep scaffold mapping details
    scaffMap = {}

    #get scaffold details for first sequence
    listScaffs1Range = (getScaffsDetails(scaffsFile1Path))
    coordScaff1Dict = getConvScaffCoordRange(listScaffs1Range)
    #print coordScaff1Dict
    
    #get scaffold details for second sequence
    listScaffs2Range = (getScaffsDetails(scaffsFile2Path))
    coordScaff2Dict = getConvScaffCoordRange(listScaffs2Range)
    #print coordScaff2Dict


    coordRefDict = coordScaff1Dict
    coordQueryDict = coordScaff2Dict
    #combine the coordinate infos from both of above sequence
    coordScaffDict = dict(coordScaff1Dict.items() + coordScaff2Dict.items()) 


    totalHits = 0
    
    #parse the directory to generate the hit maps for each scaffold
    dirContents = os.listdir(scaffDir)
    for fileName in dirContents:
        if fileName.endswith('fasta.out'):
            filePath = os.path.join(scaffDir, fileName)
            if os.path.isfile(filePath):
                (refScaffName, mappingInfos) = getScaffMappedList(filePath,\
                                                                      coordScaffDict,\
                                                                      minMatchLen)
                if refScaffName:
                    scaffMap[refScaffName] = mappingInfos
                    totalHits += len(mappingInfos)
    print 'total hits: ', totalHits
    return scaffMap

def prepareAdjacencyLists(scaffMap):
    scaffNames = scaffMap.keys()
    refAdjacencyList = {}
    queryAdjacencyList = {}
    for refScaffName, mappingInfos in scaffMap.iteritems():
        for mappingInfo in mappingInfos:
            #mappingInfo[1] contains query scaffold name
            queryScaffName = mappingInfo[1]

            if refScaffName not in refAdjacencyList:
                refAdjacencyList[refScaffName] = [queryScaffName]
            else:
                refAdjacencyList[refScaffName].append(queryScaffName)

            if queryScaffName not in queryAdjacencyList:
                queryAdjacencyList[queryScaffName] = [refScaffName]
            else:
                queryAdjacencyList[queryScaffName].append(refScaffName)
    return refAdjacencyList, queryAdjacencyList


def removeOneOneMapping(refAdjList, queryAdjList):
    refNodes = refAdjList.keys()
    for refNode in refNodes:
        neighbors = refAdjList[refNode]
        if len(set(neighbors)) == 1:
            singleNeighbor = neighbors[0]
            #check if in queryAdjList neighbor maps to node only
            if len(set(queryAdjList[singleNeighbor])) == 1 and\
                    refNode in queryAdjList[singleNeighbor]:
                #found one - one mapping
                del refAdjList[refNode]
                del queryAdjList[singleNeighbor]
    return refAdjList, queryAdjList


#plot cross minimized by calling heuristics
def plotCrossMinimizedOrdering(scaffMap):

    refAdjacencyList, queryAdjacencyList = prepareAdjacencyLists(scaffMap)
    removeOneOneMapping(refAdjacencyList, queryAdjacencyList)
    refList = refAdjacencyList.keys()
    refList.sort()
    queryList = queryAdjacencyList.keys()
    queryList.sort()
    #print refList, queryList
    scaffMapPlotter.plotFromLists(refList,\
                                      queryList,\
                                      refAdjacencyList)

    refOrderList, queryOrderList =\
        crossingMinimization.minimumCrossingOrdering(refAdjacencyList,\
                                                         queryAdjacencyList)
    #print refOrderList, queryOrderList
    scaffMapPlotter.plotFromLists(refOrderList, queryOrderList,\
                                      refAdjacencyList)

