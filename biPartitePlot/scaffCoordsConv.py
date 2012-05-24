import math
import os

"""convert scaffold mapping to another scaffold coordinates mapping which can
eventually be plotted """

#class to hold some constants, which won't be change while executing
class ScaffConstants:

    #factor specifying how many bases forms a dot
    ScaleFactor = 1

    #columns specifying start and end positions of matching regions of ref
    RefStartCol = 5 - 1
    RefEndCol = 6 - 1
    
    #column specifying reference length
    RefLenCol = 4 - 1

    #column specifying ref name
    RefNameCol =  2 - 1
    
    #column specifying query length
    QueryLenCol = 9 - 1 

    #column specifying query name
    QueryNamecol = 7 - 1
    
    #columns specifying start and end positions of matching regions of query
    QueryStartCol = 10 - 1
    QueryEndCol = 11 - 1

    #stats file scaff name
    StatsNameCol = 1 - 1

    #stats file scaff length
    StatsLengthCol = 2 - 1

#passed list in format ('scaffName', 'len)
#return a dict in format scaffName -> (start, end, len)
def getConvScaffCoordRange(listScaffsRange):
    #TODO may need to sort in specific order
    #list to contain (scaffName, start, range)
    coordScaffsDict = {}
    prevEnd = 0
    for (scaffName, len) in listScaffsRange:
        newStart = prevEnd + 1
        newEnd = math.ceil(float(newStart + (len - 1))\
                               /ScaffConstants.ScaleFactor)
        coordScaffsDict[scaffName] = (newStart, newEnd, len)
        prevEnd = newEnd
    print scaffName, prevEnd
    return coordScaffsDict


def getNewCoordsAfterSwap(scaff1Name, scaff2Name, oldListScaffsRange):
    scaff1Ind = -1
    scaff2Ind = -1
    i = 0
    newCoordScaffsDict = {}
    for (scaffName, len) in oldListScaffsRange:
        if scaffName == scaff1Name:
            scaff1Ind = i
        if scaffName == scaff2Name:
            scaff2Ind = i
    if scaff1Ind != -1 and scaff2Ind != -1:
        #swap these indices and make new list range
        oldListScaffsRange[scaff1Ind], oldListScaffsRange[scaff2Ind]\
            = oldListScaffsRange[scaff2Ind], oldListScaffsRange[scaff1Ind]
        #and get the new mappings based on new coordinate scale
        newCoordScaffsDict = getConvScaffCoordRange(oldListScaffsRange)
        if len(newCoordScaffDict) == 0:
            print 'some error occured while genearating the new coordinates'
    return (oldListScaffsRange, newCoordScaffsDict)



#parse the pairwise scaffolds
def performPairwiseScaffFlips(scaffMap, oldListScaffRange, oldCoordScaffsDict):
    scaffNameKeys = scaffMap.keys()
    prevScaffName = scaffNameKeys[0]
    for currScaffName in scaffNameKeys[1:]:
        intersectCount = countIntersect(prevscaffname, currScaffName, scaffMap)
        if intersectCount > 0:
            #swap scaffs
            newListScaffRange, newCoordScaffsDict = getNewCoordsAfterSwap(\
                prevscaffname, currScaffName, oldListScaffRange)
            #get new mapping info after swap
            newPrevMappingInfo = getNewScafMappingInfo(prevScaffName,\
                                                           oldCoordScaffsDict, \
                                                           newCoordScaffsDict,\
                                                           scaffMap[prevScaffName])
            newCurrMappingInfo = getNewScafMappingInfo(currScaffName,\
                                                           oldCoordScaffsDict, \
                                                           newCoordScaffsDict,\
                                                           scaffMap[prevScaffName])
            newCustomMap = { prevScaffName: newPrevMappingInfo,\
                                currScaffName: newCurrMappingInfo }
            #get the intersection count after swap
            newIntersectCount = countIntersect(prevscaffname, currScaffName,\
                                                   newCustomMap)
            if newIntersectCount < intersectCount:
                #for this pair we saw some decrease in count of intersection
                oldListScaffRange = newListScaffRange
                oldCoordScaffsDict = newCoordScaffsDict
                scaffMap[prevscaffname]  = newPrevMappingInfo
                scaffMap[currScaffName] = newCurrMappingInfo
    return (oldListScaffRange, oldCoordScaffsDict, scaffMap)  
            


#based on the new mapping transformed the old matching regions of scaffold 
def getNewScafMappingInfo(scaffName, oldCoordScaffsDict, newCoordScaffsDict,\
                              mappingInfos ):
    oldStart = oldCoordScaffsDict[scaffName][0]
    newStart = newCoordScaffsDict[scaffName][0]

    for i in range(len(mappingInfos)):
        refTranslatedCoord = mappingInfos[i][0]
        refTranslatedCoord = refTranslatedCoord - oldStart + newStart
        mappingInfo[i][0] = refTranslatedCoord
    return mappingInfos


#intersection of two lines given their end y's
#(y1,y2) are y's of one line endpoint ||ly (y3, y4)
def isIntersect(y1, y2, y3, y4):
    diff1 = y1- y3
    diff2 = y2 - y4
    if (diff1*diff2) >= 0:
        return True
    else:
        return False
    

#count intersection between two scaffold
#scaffMap: name -> [(refTranslatedCoord, queryScaffName, \
#    queryTranslatedCoord, refMatchedLen), ... ]
def countIntersect(scaff1Name, scaff2Name, scaffMap):
    intersectionCount = 0
    allScaff1Hits = scaffMap[scaff1Name]
    allScaff2Hits = scaffMap[scaff2Name]
    for scaff1Hit in allScaff1Hits:
        scaff1RefCoord = scaff1Hit[0]
        scaff1QueryCoord = scaff1Hit[2]
        for scaff2Hit in allScaff2Hits:
            scaff2RefCoord = scaff2Hit[0]
            scaff2QueryCoord = scaff2Hit[2]
            if isIntersect(scaff1RefCoord, scaff1QueryCoord,\
                               scaff2RefCoord, scaff2QueryCoord):
                #intersection found
                intersectionCount += 1
    return intersectionCount
    

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
def getScaffMappedList(scaffMapFilePath, coordScaffsDict):
    mappingInfos = []
    refScaffName = ''
    try:
        scaffMapFile = open(scaffMapFilePath, 'r')
        header = scaffMapFile.readline()
        for line in scaffMapFile:
            cols = (line.rstrip('\n')).split()
            coords = genCoordsRefQuery(cols, coordScaffsDict)
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
            listScaffsRange.append((cols[ScaffConstants.StatsNameCol],\
                                        float(cols[ScaffConstants.StatsLengthCol])))
        scaffsFile.close()
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)
    return listScaffsRange

def parseScaffDirNGetMapInfo(scaffDir, scaffsFile1Path, scaffsFile2Path):

    #dictionary to keep scaffold mapping details
    scaffMap = {}

    #get scaffold details for first sequence
    listScaffs1Range = getScaffsDetails(scaffsFile1Path)
    coordScaff1Dict = getConvScaffCoordRange(listScaffs1Range)
    #print coordScaff1Dict
    
    #get scaffold details for second sequence
    listScaffs2Range = getScaffsDetails(scaffsFile2Path)
    coordScaff2Dict = getConvScaffCoordRange(listScaffs2Range)
    #print coordScaff2Dict
    
    #combine the coordinate infos from both of above sequence
    coordScaffDict = dict(coordScaff1Dict.items() + coordScaff2Dict.items()) 

    #parse the directory to generate the hit maps for each scaffold
    dirContents = os.listdir(scaffDir)
    for fileName in dirContents:
        if fileName.endswith('fasta.out'):
            filePath = os.path.join(scaffDir, fileName)
            if os.path.isfile(filePath):
                (refScaffName, mappingInfos) = getScaffMappedList(filePath,\
                                                                 coordScaffDict)
                if refScaffName:
                    scaffMap[refScaffName] = mappingInfos
    return scaffMap
        
