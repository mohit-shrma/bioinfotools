""" this calculates %ge strngth of each scaffold matching to a other scaffold 
and order them in descending order  """
import sys
import operator

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
            print cgsScaffName, cgsScaffLen, matchInfoList
            cgsMatchInfo[cgsScaffName] = matchInfoList
        cgsScaffFile.close()    
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)
    return cgsMatchInfo

def main():
    if len(sys.argv) >= 3:
        bgiScaffLenFile = sys.argv[1]
        cgsScaffFile = sys.argv[2]
        orderByPc = int(sys.argv[3]) == 1
        bgiNameLenDict = getBgiScaffDict(bgiScaffLenFile)
        cgsMatchInfo = bgiStrengthInCgs(cgsScaffFile, orderByPc, bgiNameLenDict)
    else:
        print 'err: files missing'

if __name__ == '__main__':
    main()
