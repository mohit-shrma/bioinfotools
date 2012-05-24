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
        
