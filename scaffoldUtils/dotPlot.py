
""" try to make dotplots from a passed input file using start-end from ref and
query """

import sys
import os

import numpy as np
import matplotlib

#needed following to run on strong bad 
matplotlib.use('PS')


from pylab import *

#class to hold some constants
class DpConsts:

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


#generate dotplot from the file
def plotAlignment(alignmentIpFileName, refCoords, queryCoords):

    #get the file name for plot
    plotFileName = os.path.basename(alignmentIpFileName).split('.')[0]

    #get the file dir
    plotFileDir = os.path.dirname(alignmentIpFileName)
    
    #initialize py plot for non interactive backend
    matplotlib.use('Agg')

    #needed following to run on strong bad
    #indicate to pyplot that we have new figure
    #figure()

    with open(alignmentIpFileName, 'r') as alignIpFile:
        header = alignIpFile.readline()
        for line in alignIpFile:
            line = line.rstrip('\n').split()

            refScaffName = line[DpConsts.RefNameCol]
            refStart = refCoords[refScaffName][0]\
                + int(line[DpConsts.RefStartCol]) - 1
            refEnd = refCoords[refScaffName][0]\
                + int(line[DpConsts.RefEndCol]) - 1

            queryScaffName = line[DpConsts.QueryNameCol]
            queryStart = queryCoords[queryScaffName][0]\
                + int(line[DpConsts.QueryStartCol]) - 1
            queryEnd = queryCoords[queryScaffName][0]\
                + int(line[DpConsts.QueryEndCol]) - 1

            #identify  rev strand, -ve slope -> rev strand, +ve slope -> fwd strand  
            slope = -101
            if refEnd - refStart != 0:
                slope = float(queryEnd - queryStart) / float(refEnd - refStart)
                
            plotColor = ''    
            #plot the line between start and end points
            if slope == -101:
                plotColor = 'b'
            elif slope >= 0:
                plotColor = 'r'
                #if slope != 1:
                #    print '+ve slope found: ', refScaffName, [refStart, refEnd], queryScaffName, [queryStart, queryEnd]
            else:
                #print '-ve slope found: ', refScaffName, [refStart, refEnd], queryScaffName, [queryStart, queryEnd]
                plotColor = 'g'

            plot([refStart, refEnd], [queryStart, queryEnd], color = plotColor)


    ymin, ymax = ylim()   # return the current ylim
    ylim(-1, ymax)
    #needed 'ps' format to run on strongbad
    savefig(os.path.join(plotFileDir + plotFileName + '.ps'), format='ps')

    
#return reference and query coordinates range from o/p file
def getScaffCoordsDict(alignmentIpFileName):

    scaffsRefLenDict = {}
    scaffsQueryLenDict = {}

    with open(alignmentIpFileName, 'r') as alignIpFile:
        header = alignIpFile.readline()
        for line in alignIpFile:
            line = line.rstrip('\n').split()

            refScaffName = line[DpConsts.RefNameCol]
            refLen = int(line[DpConsts.RefLenCol])

            if refScaffName not in scaffsRefLenDict:
                scaffsRefLenDict[refScaffName] = refLen

            queryScaffName = line[DpConsts.QueryNameCol]
            queryLen  = int(line[DpConsts.QueryLenCol])
            
            if queryScaffName not in scaffsQueryLenDict:
                scaffsQueryLenDict[queryScaffName] = queryLen

    scaffRefLens = []
    for scaffName, scaffLen in scaffsRefLenDict.iteritems():
        scaffRefLens.append((scaffName, scaffLen))
    sortedScaffRefLens = sorted(scaffRefLens,\
                                    key=lambda scaffRefLen: scaffRefLen[1],\
                                    reverse=True)

    refCoords = {}
    prevEnd = 0
    for refNameLen in sortedScaffRefLens:
        refName = refNameLen[0]
        refLen = refNameLen[1]
        #TODO: confirm mummer output whether start from 0 or not
        start = prevEnd + 1
        end = start + refLen - 1
        refCoords[refName] = (start, end)
        prevEnd = end
    
    scaffQueryLens = []
    for scaffName, scaffLen in scaffsQueryLenDict.iteritems():
        scaffQueryLens.append((scaffName, scaffLen))
    sortedScaffQueryLens = sorted(scaffQueryLens,\
                                      key=lambda scaffQueryLen: scaffQueryLen[1],\
                                      reverse=True)
    
    queryCoords = {}
    prevEnd = 0
    for queryNameLen in sortedScaffQueryLens:
        queryName = queryNameLen[0]
        queryLen = queryNameLen[1]
        #TODO: confirm mummer output whether start from 0 or not
        start = prevEnd + 1
        end = start + queryLen - 1
        queryCoords[queryName] = (start, end)
        prevEnd = end

    return refCoords, queryCoords

                
def main():
    argLen = len(sys.argv)
    if argLen >= 2:
        alignmentIpFileName = sys.argv[1]
        refCoords, queryCoords = getScaffCoordsDict(alignmentIpFileName)
        plotAlignment(alignmentIpFileName, refCoords, queryCoords)
    else:
        print 'err: files missin'




if __name__ == '__main__':
    main()

