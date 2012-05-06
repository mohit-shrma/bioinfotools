"""this extract matching region detected by mummer-suffix tree algo,
passed file containing contigs name start and ending matching regions,
fasta file containing desired contigs,
output file to whixh to write matched regions"""

import sys

""" matching dict -> 'contigs name'-> {'start': x, 'end':y}"""
def extractMatchedRegion(matchingDict, contigsFastaFileName, opFileName):
    try:
        contigsFile = open(contigsFastaFileName, 'r')
        opFile = open(opFileName, 'w')
        line=contigsFile.readline()
        while line:
            if line.startswith('>'):
                #detected header
                header = line.lstrip('>').rstrip('\n').split()[0]
                if header in matchingDict:
                    #current contig one of matching contig
                    #extract the matching regions from it
                    contigs = contigsFile.readline().rstrip('\n')
                    for tempRange in matchingDict[header]:
                        start = tempRange[0] - 1
                        end = tempRange[1] - 1
                        if end < start: 
                            #contigs matching in reverse direction
                            start, end = end, start
                        matched = contigs[start:end+1]
                        opFile.write('>')
                        opFile.write(header+'_'+str(start+1)+'_'+str(end+1))
                        opFile.write('\n')
                        opFile.write(matched)
                        opFile.write('\n')                    
                    #don't need this key, can delete it
                    del matchingDict[header]
                    if len(matchingDict) == 0:
                        #all the dict is processed exit the loop
                        break
            line = contigsFile.readline()
        contigsFile.close()
        opFile.close()
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)

"""will check if any conflict among ranges"""
def isConflict(range1, range2):
    range1Start = range1[0]
    range1End =  range1[1]
    range2Start = range2[0]
    range2End = range2[1]
    if (range1End < range2Start or range1Start > range2End):
        return False
    else:
        return True


""" will merge two conflicted ranges"""
def mergeRanges(range1, range2):
    if (isConflict(range1, range2)):
        range1Start = range1[0]
        range1End =  range1[1]
        range2Start = range2[0]
        range2End = range2[1]
        if range1Start < range2Start:
            newStart = range1Start
        else:
            newStart = range2Start
            
        if range1End > range2End:
            newEnd = range1End
        else:
            newEnd = range2End
        return [newStart, newEnd]
    else:
        return []


""" check if query range is in conflict with range list and
return the merged one in that case"""
def checkAndMergeRange(rangeList, queryRange):
    conflicted = False
    for i in range(len(rangeList)):
        tempRange = rangeList[i]
        if (isConflict(queryRange, tempRange)):
            #conflict and need to be merged
            conflicted = True
            newRange = mergeRanges(queryRange, tempRange)
            #replace the current range
            rangeList[i] = newRange
            break
    if not conflicted:
        rangeList.append(queryRange)
        rangeList.sort()
    else:
        #conflicted, make sure full list is out of conflict
        rangeList.sort()
        for i in range(len(rangeList)-1):
            rangePrev = rangeList[i]
            rangeCurr = rangeList[i+1]
            if isConflict(rangePrev, rangeCurr):
                mergedRange = mergeRanges(rangePrev, rangeCurr)
                if len(mergedRange) > 0:
                    rangeList[i] = []
                    rangeList[i+1] = mergedRange
        #clear the empty ranges
        retList = []
        for tempRange in rangeList:
            if len(tempRange) > 0:
                retList.append(tempRange)
        rangeList = retList
    return rangeList
            
        

""" returns a matching dictionary containg positions of all matched regions"""
def createMatchingDict(matchFileName):
    matchingDict = {}
    headerColNo = 1 -1 #-1 as zero based indexing
    startColNo = 2 -1
    endColNo = 3 -1
    try:
        matchFile = open(matchFileName, 'r')
        header = matchFile.readline()
        for line in matchFile:
            line = line.rstrip('\n')
            if line:
                columns = line.split()
                header = columns[headerColNo]
                start = int(columns[startColNo])
                end = int(columns[endColNo])
                if end < start:
                    start, end = end, start
                if header in matchingDict:
                    #if already existing then append the new range in
                    #dict
                    #check for conflict and merge if any conflict
                    matchingDict[header] = checkAndMergeRange(\
                        matchingDict[header],\
                            [start, end])
                else:
                    matchingDict[header] = [[start, end]]
        matchFile.close()
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)
    return matchingDict


def main():
    if len(sys.argv) >= 3:
        matchedFileName = sys.argv[1]
        contigsFileName = sys.argv[2]
        opFileName = sys.argv[3]
        matchingDict = createMatchingDict(matchedFileName)
        extractMatchedRegion(matchingDict, contigsFileName, opFileName)
    else:
        print 'err: files missing'

if __name__ == '__main__':
    main()


