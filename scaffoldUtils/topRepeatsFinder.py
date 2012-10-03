""" find top repeats in one sequence and then look where it occurs in other
sequence and how many times  """

import sys
import os
import operator

#TODO: think for reverse alignment
#TODO: think of output in different format too like zstart and others

class LastzConsts:

    #
    #TODO:

    #reference identity match
    RefIdCol = 12

    #refernce name col
    RefNameCol = 1

    #reference start col
    RefStartCol = 4

    #reference end col
    RefEndCol = 5

    #reference length col
    RefLenCol = 3

    #query identity match
    QueryIdCol = 12
    
    #query name col
    QueryNameCol = 6

    #query start col
    QueryStartCol = 9

    #query end col
    QueryEndCol = 10
    
    #query length col
    QueryLenCol= 8

    #scaff file ext
    LastzOutExt = 'fasta.out'

    #safe Offset Const
    SafeOffsetConst = 50000

    
class MummerConsts:

    #TODO: reference matched length col
    RefMatchLenCol = 4

    #TODO: reference identity match
    RefIdCol = 6

    #refernce name col
    RefNameCol = 11

    #reference start col
    RefStartCol = 0

    #reference end col
    RefEndCol = 1

    #reference length col
    RefLenCol = 7
    
    #query name col
    QueryNameCol = 12

    #query start col
    QueryStartCol = 2

    #query end col
    QueryEndCol = 3
    
    #query length col
    QueryLenCol= 8


    
""" get hits length and return hit in dict with
start and end as key & number of repetitions as value """
def getHits(mummerOpFileName, minMatchLen):
    #get hits length in a list
    hits = []
    hitDict = {}
    with open(mummerOpFileName, 'r') as opFile:

        header = opFile.readline()

        for line in opFile:

            cols = line.rstrip('\n').split()
            refName = cols[MummerConsts.RefNameCol]
            refStart = int(cols[MummerConsts.RefStartCol])
            refEnd = int(cols[MummerConsts.RefEndCol])
            queryStart = int(cols[MummerConsts.QueryStartCol])
            queryEnd = int(cols[MummerConsts.QueryEndCol])
            refMatchLen = int(cols[MummerConsts.RefMatchLenCol])
        
            #identify if not on diagonal and min match len satisfied
            if (refStart != queryStart or refEnd != queryEnd) \
                    and refMatchLen >= minMatchLen:
                hitLen = int(cols[MummerConsts.RefMatchLenCol])
                hits.append(hitLen)
                hitKey = refName + ':' + str(refStart) + ':' + str(refEnd)
                if hitKey not in hitDict:
                    hitDict[hitKey] = 1
                else:
                    hitDict[hitKey] += 1
            
    #sort the hits
    hits.sort()
    return hits, hitDict



def findTopRepeats(hitDict, numTopRepeats):
    #sort dict by value of hit in dict
    sortedHits = sorted(hitDict.iteritems(), key=operator.itemgetter(1),\
                            reverse=True)

    #pick the top numRepeats from list
    topRepeats = sortedHits[:numTopRepeats]

    #convert string to numerical range from key
    hitCoords = []

    for hitCoordStr, count in topRepeats:
        hitCoordStr = hitCoordStr.split(':')
        hitCoords.append( ( hitCoordStr[0], int(hitCoordStr[1]),\
                                int(hitCoordStr[2])) )
    
    return topRepeats, hitCoords



def findQueryHits(refFastaOutDir, hitCoords):
    queryHitCoords = []
    for scaffName, refStart, refEnd in hitCoords:
        #open scaffName.fasta.out and
        #look for query scaff regions where this region matches
        scaffFilePath = os.path.join(refFastaOutDir, scaffName + '.' \
                                     + LastzConsts.LastzOutExt)
        with open(scaffFilePath, 'r') as scaffFile:
            header = scaffFile.readline()
            for line in scaffFile:
                cols = line.rstrip('\n').split()
                start = int(cols[LastzConsts.RefStartCol])
                end = int(cols[LastzConsts.RefEndCol])
                if refStart >= start and refEnd <= end:
                    #interval lies inside current record
                    #get current query details
                    queryName = cols[LastzConsts.QueryNameCol]
                    queryStart = int(cols[LastzConsts.QueryStartCol])
                    queryEnd = int(cols[LastzConsts.QueryEndCol])
                    queryHitCoords.append((queryName, queryStart, queryEnd))
                elif refStart <= start + LastzConsts.SafeOffsetConst:
                    #now too ahead in search of region so quit in midway
                    break
    return queryHitCoords


#return next non diagonal match
def getAlignNameStartEnd(file):

    refStart = None
    refEnd = None
    refName = None

    queryStart = None
    queryEnd = None
    queryName = None

    nonDiag = False
    
    for line in file:
    
        cols = line.rstrip('\n').split()

        refStart = int(cols[MummerConsts.RefStartCol])
        refEnd = int(cols[MummerConsts.RefEndCol])
        refName = cols[MummerConsts.RefNameCol]
        
        queryStart = int(cols[MummerConsts.QueryStartCol])
        queryEnd = int(cols[MummerConsts.QueryEndCol])
        queryName = cols[MummerConsts.QueryNameCol]


        if refStart != queryStart or refEnd != queryEnd or refName != queryName:
            #non diagonal entry
            nonDiag = True
            break

    if nonDiag:
        return refName, refStart, refEnd, queryName, queryStart, queryEnd
    else:
        return None, None, None, None, None


""" count occurence of query hits in query self alignment """
def countQueryHitOccurence(querySelfAlignFileName, queryHitcoords):

    #find indice at which digit starts in query scaffname
    digitInd = -1
    tempName = queryHitcoords[0][0]
    for i in range(len(tempName)):
        if tempName[i].isdigit():
            digitInd = i
            break
        
    #sort queryHitCoords by numerical suffix of name at 0 index
    sortedQueryHitCoords = sorted(queryHitCoords,\
                                    key = lambda coord:int(coord[0][digitInd:]))
    queryCoordInd = 0

    #region hit storage
    #stored as [ ( (nam, start, end), (nam, start, end) ), ... ]
    foundHits = []
    
    with open(querySelfAlignFileName, 'r') as querySelfAlignFile:

        header = querySelfAlignFile.readline()
        queryAlignStart, queryAlignEnd, queryAlignName, \
            rAlignStart, rAlignEnd, rAlignName\
            = getAlignNameStartEnd(querySelfAlignFile)

        while True and queryCoordInd < len(queryHitCoords)\
                and rAlignStart != None:

            currQueryHitName = sortedQueryHitCoords[queryCoordInd][0]
            currQueryHitStart = sortedQueryHitCoords[queryCoordInd][1]
            currQueryHitEnd = sortedQueryHitCoords[queryCoordInd][2]

            if currQueryHitName == queryAlignName:
                #if desired hit name matches align name
                if currQueryHitStart >= queryAlignStart and\
                        currQueryHitEnd <= queryAlignEnd:
                    #region is contained in a hit
                    #note down the region found and what it is found as
                    foundHits.append(( \
                            (queryAlignName, queryAlignStart, queryAlignEnd),\
                                (rAlignName, rAlignStart, rAlignEnd) ))
                    #move on to next desired hit
                    queryCoordInd += 1
                elif currQueryHitStart < queryAlignStart:
                    #advance to next desired hit
                    queryCoordInd += 1
                elif currQueryHitStart > queryAlignStart:
                    #advance to next record in file
                    queryAlignStart, queryAlignEnd, queryAlignName, \
                        rAlignStart, rAlignEnd, rAlignName\
                        = getAlignNameStartEnd(querySelfAlignFile)
            else:
                #desired hit name not matches align name
                while currQueryHitName != queryAlignName:
                    queryAlignStart, queryAlignEnd, queryAlignName, \
                        rAlignStart, rAlignEnd, rAlignName\
                        = getAlignNameStartEnd(querySelfAlignFile)
                    if rAlignStart != None:
                        break

    return foundHits



def main():
    argLen = len(sys.argv)
    if argLen >= 4:
        mummerOpFileName = sys.argv[1]
        minMatchLen = int(sys.argv[2])
        refFastaOutDir = sys.argv[3]
        hits, hitDict = getHits(mummerOpFileName, minMatchLen)
        topRepeats, hitCoords = findTopRepeats(hitDict, 5)
        print 'topRepeats: ',topRepeats
        queryHitCoords = findQueryHits(refFastaOutDir, hitCoords)
        #TODO: this is coming empty
        print 'queryHitCoords: ', queryHitCoords
    else:
        print 'err: files missin'
        



if __name__ == '__main__':
    main()

