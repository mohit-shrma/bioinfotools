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

    
#return the matching details for currrent match
def genCoordsRefQuery(cols):

    refScaffName = cols[ScaffConstants.RefNameCol]
    refStart = float(cols[ScaffConstants.RefStartCol])
    refEnd = float(cols[ScaffConstants.RefEndCol])
    refCoord = math.ceil(((refStart + refEnd) / 2) / ScaffConstants.ScaleFactor)
    #TODO: check whether -1 needs to be added
    refMatchedLen = refEnd - refStart
     
    queryScaffName = cols[ScaffConstants.QueryNamecol]
    queryStart = float(cols[ScaffConstants.QueryStartCol])
    queryEnd = float(cols[ScaffConstants.QueryEndCol])
    queryCoord = math.ceil(((queryStart + queryEnd) / 2)\
                               / ScaffConstants.ScaleFactor)

    return ([refStart, refEnd], queryScaffName,\
                [queryStart, queryEnd], refMatchedLen)
    

#tranform the mapping from ref to query, in new coords format
def getScaffMappedList(scaffMapFilePath,  minMatchedLen = 5000):
    mappingInfos = []
    refScaffName = ''
    try:
        scaffMapFile = open(scaffMapFilePath, 'r')
        header = scaffMapFile.readline()
        for line in scaffMapFile:
            cols = (line.rstrip('\n')).split()
            coords = genCoordsRefQuery(cols)
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

    totalHits = 0
    
    #parse the directory to generate the hit maps for each scaffold
    dirContents = os.listdir(scaffDir)
    for fileName in dirContents:
        if fileName.endswith('fasta.out'):
            filePath = os.path.join(scaffDir, fileName)
            if os.path.isfile(filePath):
                (refScaffName, mappingInfos) = getScaffMappedList(filePath,\
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


#remove independent one-to-many mappings these dont have any intersection with\
#others and can be considered independently
def removeOneToManyMapping(refAdjList, queryAdjList):
    refNodes = refAdjList.keys()
    for refNode in refNodes:
        neighbors = set(refAdjList[refNode])
        neighborDelCount = 0
        for neighbor in neighbors:
            if len(set(queryAdjList[neighbor])) == 1 and\
                    refNode in queryAdjList[neighbor]:
                neighborDelCount += 1
        if neighborDelCount == len(neighbors):
            #found one-many mapping
            del refAdjList[refNode]
            for neighbor in neighbors:
                del queryAdjList[neighbor]
    return refAdjList, queryAdjList
    

#display regions in specified order, depending on value of printRef
def displayMatchingRegion(scaffMap, refOrderList, refAdjList,\
                              queryOrderList, queryAdjList,\
                              printRef):
    if printRef:
        #print by refList order
        for refName in refOrderList:
            for mappingInfo in scaffMap[refName]:
            #mappingInfo is of following form    
            # ([refStart, refEnd], queryScaffName,
            #  [queryStart, queryEnd], refMatchedLen)
                print refName, mappingInfo[0][0], mappingInfo[0][1],\
                    mappingInfo[1], mappingInfo[2][0], mappingInfo[2][1],\
                    mappingInfo[3]
    else:
        #print by queryList order
        for queryName in queryOrderList:
            refMatchingScaffs = queryAdjList[queryName]
            for refName in set(refMatchingScaffs):
                for mappingInfo in scaffMap[refName]:
                #mappingInfo is of following form    
                # ([refStart, refEnd], queryScaffName,
                #  [queryStart, queryEnd], refMatchedLen)
                    if queryName == mappingInfo[1]:
                        print queryName, mappingInfo[2][0], mappingInfo[2][1],\
                            refName, mappingInfo[0][0], mappingInfo[0][1],\
                            mappingInfo[3]


                        
#plot cross minimized by calling heuristics
def plotCrossMinimizedOrdering(scaffMap):

    #try to plot before removing 1-1 or 1-many mappings
    refAdjacencyList, queryAdjacencyList = prepareAdjacencyLists(scaffMap)
    refList = refAdjacencyList.keys()
    refList.sort()
    queryList = queryAdjacencyList.keys()
    queryList.sort()
    scaffMapPlotter.plotFromLists(refList,\
                                      queryList,\
                                      refAdjacencyList)
    #remove contained in itself one-to-many mapping before
    #reordering
    removeOneToManyMapping(refAdjacencyList, queryAdjacencyList)
    removeOneToManyMapping(queryAdjacencyList, refAdjacencyList)

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
    
    """
    print 'refOrderList: ', refOrderList, '\n'
    print 'queryOrderList: ', queryOrderList, '\n'
    print 'refAdjacencyList: ', refAdjacencyList, '\n'
    print 'queryAdjacencyList: ', queryAdjacencyList, '\n'

    displayMatchingRegion(scaffMap, refOrderList, refAdjacencyList,\
                              queryOrderList, queryAdjacencyList,\
                              False)"""
    
    #print refOrderList, queryOrderList
    scaffMapPlotter.plotFromLists(refOrderList, queryOrderList,\
                                      refAdjacencyList)
    
