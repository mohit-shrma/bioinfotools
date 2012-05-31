from pylab import *
import numpy as np
import coordsConverter
import sys

class PlotConsts:

    #distance b/w two coords i.e |X2 -X1|
    XSep = 100

    #default param to control thickness of line
    Thick = 2
    
#generate the plot for passed scaffMap
#scaffMap dict, scaffName -> [(refTranslatedCoord, queryScaffName,\
#                queryTranslatedCoord, refMatchedLen), ...]
def generatePlot(scaffMap, minMatchedLen, outFile = ''):
    
    for scaffName, mappingInfos in scaffMap.iteritems():
        #print 'plotting ' + scaffName, 'minMatchedLen: ' + str(minMatchedLen)
        for mapInfo in mappingInfos:
            refMatchedLen = mapInfo[3] 
            if refMatchedLen > minMatchedLen:
                #join (0, mapInfo[0]) -> (0+XSep, mapInfo[2])
                vertices = np.array([\
                        [0, mapInfo[0]],\
                            [0+PlotConsts.XSep, mapInfo[2]]\
                            ])

                if refMatchedLen > 50000:
                    color = 'r'
                elif refMatchedLen > 25000:
                    color = 'g'
                elif refMatchedLen > 15000: 
                    color = 'b'
                else:
                    color = 'm'

                plot(vertices[:,0], vertices[:,1], color = color)

    if not outFile:
        show()
    else:
        savefig(outFile)

#plot from adjacency list with indices representing vertices,\
#and value at these indices representing query node it maps too
def plotFromArrayAdjList(adjListA, adjListB, minMatchLen = 0):
    intersectionCount, numLines = \
        coordsConverter.getIntersectionCountFromAdj(adjListA)
    print 'intersection count: ', intersectionCount
    print 'num lines: ', numLines
    for aNode in adjListA:
        for aNeighbor on adjListA[aNode]:
            vertices = np.array([[0, aNode],[0+PlotConsts.XSep, aNeighbor]])
            plot(vertices[:, 0], vertices[:, 1], color = 'g')
            print vertices
    ymin, ymax = ylim()   # return the current ylim
    ylim(0, ymax)
    show()
            

        
def plotFromLists(nodesA, nodesB, adjListA, minMatchLen = 0):
    nodesACoord = coordsConverter.getCoordinatesDict(nodesA)
    nodesBCoord = coordsConverter.getCoordinatesDict(nodesB)
    #print adjListA
    #print nodesA
    #print nodesACoord
    #print nodesB
    #print nodesBCoord
    print 'made nodesACoord, nodesBCoord', len(nodesACoord), len(nodesBCoord)
    sys.stdout.flush()
    intersectionCount, numLines = coordsConverter.getIntersectionCount(nodesA,\
                                                                   nodesACoord,\
                                                                   nodesBCoord,\
                                                                   adjListA)
    print 'plotFromLists: Intersection count: ', minMatchLen, intersectionCount
    print 'plotFromLists: Num lines: ', minMatchLen, numLines
    sys.stdout.flush()
    #on koronis no pylab module installed, take care of that too,
    #so no plotting code
    
    for node in nodesA:
        midPtNodeA = (nodesACoord[node][0] + nodesACoord[node][1])/2
        for neighbor in adjListA[node]:
            midPtNeighborB = (nodesBCoord[neighbor][0]\
                                  + nodesBCoord[neighbor][1])/2
            vertices = np.array([[0, midPtNodeA],\
                                     [0+PlotConsts.XSep, midPtNeighborB]])
            plot(vertices[:,0], vertices[:,1], color = 'r')
            print vertices
    ymin, ymax = ylim()   # return the current ylim
    ylim(0, ymax)
    show()
    
