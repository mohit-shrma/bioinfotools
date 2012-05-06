""" this calculates %ge strngth of each scaffold matching to a other scaffold 
and order them in descending order  """
""" python postIntervalProcess.py ~/Documents/spring12/hugroup/koronis/2012Apr9500RefBGIQueryNCGR/stats.txt ~/Documents/spring12/hugroup/koronis/2012Mar15Strict500/stats3.txt ../../../chromosomalComp/bgiChroms  1"""

import sys
import operator

def getBgiScaffoldChromDict(dictFileName):
    scaffNameCol = 1 - 1
    chromCol = 2 - 1
    chromDict = {}
    try:
        dictFile = open(dictFileName, 'r')
        header = dictFile.readline()
        for line in dictFile:
            line = line.rstrip('\n').split()
            scaffName = line[scaffNameCol]
            chromName = line[chromCol]
            chromDict[scaffName] = chromName
        dictFile.close()
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)        
    return chromDict



"""get the scaffold name and size dict"""
def getBgiScaffDict(bgiScaffFileName):
    scaffNameCol = 1 - 1
    lengthCol = 2 - 1
    bgiNameLenDict = {};
    try:
        bgiScaffFile = open(bgiScaffFileName, 'r')
        header = bgiScaffFile.readline()
        for line in bgiScaffFile:
            line = line.rstrip('\n').split()
            scaffName = line[scaffNameCol]
            scaffLen = int(line[lengthCol])
            bgiNameLenDict[scaffName] = scaffLen 
        bgiScaffFile.close()
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)
    return bgiNameLenDict

""" order matching scaffold by matching length """
def bgiStrengthInCgs(cgsScaffFileName, orderByPc, bgiNameLenDict):
    cgsScaffNameCol = 1 - 1
    bgiMatchLenInfoCol = 7 - 1
    cgsScaffLenCol = 2 - 1
    cgsMatchInfo ={}
    try:
        cgsScaffFile = open(cgsScaffFileName, 'r')
        header = cgsScaffFile.readline()
        for line in cgsScaffFile:
            line = line.rstrip('\n').split()
            #get the scaffold details
            cgsScaffName = line[cgsScaffNameCol]
            cgsScaffLen = line[cgsScaffLenCol]
            #get the matching info
            if len(line) > bgiMatchLenInfoCol:
                bgiMatchLenInfo = line[bgiMatchLenInfoCol].split(',')
            else:
                bgiMatchLenInfo = []
            #now order the above info depending on specified order
            #matchInfoList conatains tri tuple values
            #(bgiScaffName, bgiScaffMatchLen, bgiScaffPc)
            matchInfoList = []
            for matchInfo in bgiMatchLenInfo:
                #matchinfo is of form <scaff name>:<match length>
                """TODO: find a sorted structure: bisect, heapQ"""
                matchInfo = matchInfo.split(':')
                matchScaffName = matchInfo[0]
                matchScaffLen = int(matchInfo[1])
                matchScaffPc = float(matchScaffLen)/bgiNameLenDict[matchScaffName]
                matchInfoList.append((matchScaffName, matchScaffLen, matchScaffPc))
            #sort matchInfoList base on desired param
            if orderByPc:
                #order by %match w.r.t bgiScaff
                matchInfoList.sort(key=operator.itemgetter(2), reverse=True)
            else:
                #order by matched Length
                matchInfoList.sort(key=operator.itemgetter(1), reverse=True)
            #print cgsScaffName, cgsScaffLen, matchInfoList
            cgsMatchInfo[cgsScaffName] = matchInfoList
        cgsScaffFile.close()    
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)
    return cgsMatchInfo

def mapChrom(chromDict, cgsMatchInfoDict):
    #map info from chromosomes to cgs scaffolds info
    cgsScaffsChromInfo = []
    for cgsScaffold, matchInfos in cgsMatchInfoDict.iteritems():
        #matchInfos is a list of tuple (bgiscaffname, matchLen, %)
        #a dict containing mapping of chromosome: matched corresponding length
        cgsScaffChromDict = {}
        for matchInfo in matchInfos:
            bgiScaffName = matchInfo[0]
            bgiScaffMatchLen = matchInfo[1]
            #bgiScaffMatch% = matchInfo[2]
            if bgiScaffName in chromDict:
                bgiScaffChrom = chromDict[bgiScaffName]
            else:
                continue
            if bgiScaffChrom in cgsScaffChromDict:
                cgsScaffChromDict[bgiScaffChrom] += bgiScaffMatchLen
            else:
                cgsScaffChromDict[bgiScaffChrom] = bgiScaffMatchLen
        cgsScaffChromTuples = [(k,v) for k,v in cgsScaffChromDict.iteritems()]
        cgsScaffChromTuples.sort(key=operator.itemgetter(1), reverse=True)
        cgsScaffsChromInfo.append((cgsScaffold, cgsScaffChromTuples)) 
        #print cgsScaffold, cgsScaffChromTuples
    cgsScaffsChromInfoSorted = sorted(cgsScaffsChromInfo, \
                                          key=lambda chromInfo: int(chromInfo[0][3:]))
    for chromInfo in cgsScaffsChromInfoSorted:
        print chromInfo
    return cgsScaffsChromInfoSorted

#compute avg. chromosome size for the passed number of rows, other wise for all rows
def computeAvgChromosomalSize(cgsScaffsChromInfo, numRows=0):
    #do till first 5 chromosomes
    if numRows == 0:
        numRows = len(cgsScaffsChromInfo)
        chromLenVec = [0.0, 0.0, 0.0, 0.0, 0.0]
    for i in range(numRows):
        for j in range(len(cgsScaffsChromInfo[i][1])):
            if j > 4:
                break
            chromLenVec[j] += cgsScaffsChromInfo[i][1][j][1]
    chromAvgVec = [num/numRows for num in chromLenVec]
    print chromLenVec
    print chromAvgVec

def main():
    if len(sys.argv) >= 4:
        bgiScaffLenFile = sys.argv[1]
        cgsScaffFile = sys.argv[2]
        bgiScaffoldDictFileName = sys.argv[3]
        orderByPc = int(sys.argv[4]) == 1
        bgiNameLenDict = getBgiScaffDict(bgiScaffLenFile)
        cgsMatchInfo = bgiStrengthInCgs(cgsScaffFile, orderByPc, bgiNameLenDict)
        bgiChromDict = getBgiScaffoldChromDict(bgiScaffoldDictFileName)
        cgiScaffsChromInfo = mapChrom(bgiChromDict, cgsMatchInfo)
        computeAvgChromosomalSize(cgiScaffsChromInfo)
    else:
        print 'err: files missing'

if __name__ == '__main__':
    main()
