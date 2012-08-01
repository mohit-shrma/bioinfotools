
""" make hits distribution for mummer alignment output """

import sys
import os

import numpy as np
import matplotlib
import numpy.numarray as na

#needed following to run on strong bad 
matplotlib.use('PS')


from pylab import *

class HitDistConsts:

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

    #maximum bin "MIN" length
    MAX_BIN_MINLEN = 110000


def getHits(mummerOpFileName, minMatchLen):
    #get hits length in a list
    hits = []
    with open(mummerOpFileName, 'r') as opFile:

        header = opFile.readline()

        for line in opFile:

            cols = line.rstrip('\n').split()

            refStart = int(cols[HitDistConsts.RefStartCol])
            refEnd = int(cols[HitDistConsts.RefEndCol])
            queryStart = int(cols[HitDistConsts.QueryStartCol])
            queryEnd = int(cols[HitDistConsts.QueryEndCol])
            refMatchLen = int(cols[HitDistConsts.RefMatchLenCol])
        
            #identify if not on diagonal and min match len satisfied
            if (refStart != queryStart or refEnd != queryEnd) \
                    and refMatchLen >= minMatchLen:
                hitLen = int(cols[HitDistConsts.RefMatchLenCol])
                hits.append(hitLen)
            
    #sort the hits
    hits.sort()
    return hits
    
    
def plotNonDiagHitDist(mummerOpFileName, minMatchLen, intervalLen):

    #get the file name for plot
    plotFileName = os.path.basename(mummerOpFileName).split('.')[0]

    #get the file dir
    plotFileDir = os.path.dirname(mummerOpFileName)
    
    #initialize py plot for non interactive backend
    matplotlib.use('Agg')

    #indicate to pyplot that we have new figure
    #needed to comment following to run on strong bad
    #figure()
    
    hits = getHits(mummerOpFileName, minMatchLen)
                
    #construct bins based on hit length strength
    #list contain each bin min value, max value given by next 1 less than
    #next in the list
    binLabels = range(0, HitDistConsts.MAX_BIN_MINLEN, intervalLen)
    binCount = [0 for i in binLabels]

    currBinInd = 0
        
    for hitLen in hits:
        #find appropriate bin index
        while (hitLen > binLabels[currBinInd+1]):
            currBinInd += 1
        binCount[currBinInd] += 1

    #start trimming bins from end till not empty
    for i in range(len(binCount)-1, -1, -1):
        if binCount[i] != 0:
            break
    if i != len(binCount) -1:
        binCount = binCount[0:i+2]
        binLabels = binLabels[0:i+2]
    
    binShortLabels = [label/1000 for label in binLabels]

    #plot bar graph of hitcount with hit labels
    xLocations = na.array(range(len(binLabels)))
    width = 0.5
    bar(xLocations, binCount,  width=width)
        
    #yticks(range(0, 8))

    xticks(xLocations, binShortLabels)
    xlim(0, xLocations[-1]+width*2)
    title("hit count distribution")
    gca().get_xaxis().tick_bottom()
    gca().get_yaxis().tick_left()

    #needed 'ps' format to run on strongbad
    savefig(os.path.join(plotFileDir + plotFileName + '.ps'), format='ps')



                
def main():
    argLen = len(sys.argv)
    if argLen >= 4:
        alignmentOpFileName = sys.argv[1]
        minMatchLen = int(sys.argv[2])
        intervalLen = int(sys.argv[3])
        plotNonDiagHitDist(alignmentOpFileName, minMatchLen, intervalLen)
    else:
        print 'err: files missin'
        



if __name__ == '__main__':
    main()



