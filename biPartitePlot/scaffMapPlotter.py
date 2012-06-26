from pylab import *
import numpy as np
import coordsConverter
import sys
import os
import matplotlib

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


#generate plot for passed scaffold        
def generateScaffPlot(scaffName, scaffMap, lengthDict, plotDir = None):
    #mappingInfo is of following form    
    # ([refStart, refEnd], queryScaffName,
    #  [queryStart, queryEnd], refMatchedLen)
    #sort by 0/refStart
    mappingInfos = scaffMap[scaffName]
    sortedMappingInfos = sorted(mappingInfos, key=lambda mapInfo: mapInfo[0][0])

    if plotDir is None:
        #not passed any directory to store plot
        #use Current directory to storeplot
        plotDir = os.path.abspath("./parallelPlots")
        if not os.path.exists(plotDir):
            os.makedirs(plotDir)
    else:
        plotDir = os.path.abspath(plotDir)
        
    queryNames = []
    for mapInfo in sortedMappingInfos:
        if mapInfo[1] not in queryNames:
            queryNames.append(mapInfo[1])
    
    prevOffset = 0
    prevQueryName = ''

    #prepare colors for different scaffold
    colors = ['g','b', 'c', 'm', 'k', 'g','b', 'c', 'm', 'k','g','b', 'c', 'm',\
                  'k', 'g','b', 'c', 'm', 'k']
    colorDict = dict(zip(queryNames, colors))
    
    #prepare coordinates for the plot
    queryNamesStart = {}
    prevEnd = 0
    for queryName in queryNames:
        queryNamesStart[queryName] = prevEnd + 1
        prevEnd = prevEnd + lengthDict[queryName]
    
    print 'plotting ', scaffName#, lengthDict[scaffName], ' .....'
    
    #initialize py plot for non interactive backend
    matplotlib.use('Agg')
    #indicate to pyplot that we have new figure
    figure()
    #get handle to axes
    ax = gca()
    #array to keep track which text plotted or not
    texted = []
    #remove x-axis
    ax.xaxis.set_visible(False)


    for mapInfo in sortedMappingInfos:
        currRefStart = mapInfo[0][0]
        currRefEnd = mapInfo[0][1]

        currQueryName = mapInfo[1]
        currQueryStart = mapInfo[2][0]
        currQueryEnd = mapInfo[2][1]

        if prevQueryName != '' and  prevQueryName != currQueryName:
            #update offset
            prevOffset += lengthDict[prevQueryName] 
            
        #plot start vertices
        verticesStart = np.array([[0, currRefStart],\
                                  [0+PlotConsts.XSep,\
                                   queryNamesStart[currQueryName]\
                                    + currQueryStart - 1]])

        #plot end vertices
        verticesEnd = np.array([[0, currRefEnd],\
                                [0+PlotConsts.XSep,\
                                 queryNamesStart[currQueryName]\
                                  + currQueryEnd - 1]])

        fill([0, 0, 0+PlotConsts.XSep, 0+PlotConsts.XSep],\
                 [currRefStart, currRefEnd,\
                      queryNamesStart[currQueryName] + currQueryEnd - 1,\
                      queryNamesStart[currQueryName] + currQueryStart - 1],\
                 colorDict[currQueryName], edgecolor=colorDict[currQueryName])

        #assign query name to plotted scaffold
        if currQueryName not in texted:
            ax.text(0+PlotConsts.XSep-5, queryNamesStart[currQueryName]\
                        + ((currQueryEnd + currQueryStart)/2) -1, currQueryName,\
                        fontsize=10)
            texted.append(currQueryName)
        
        prevQueryName = currQueryName
        #print currQueryName, lengthDict[currQueryName]
    ymin, ymax = ylim()   # return the current ylim
    ylim(-1, ymax)
    #show()
    savefig(os.path.join(plotDir, scaffName + '.png'))

    
        
#plot from adjacency list with indices representing vertices,\
#and value at these indices representing query node it maps too
def plotFromArrayAdjList(adjListA, adjListB, minMatchLen = 0):
    intersectionCount, numLines = \
        coordsConverter.getIntersectionCountFromAdj(adjListA)
    print 'intersection count: ', intersectionCount
    print 'num lines: ', numLines
    for aNode in range(len(adjListA)):
        for aNeighbor in adjListA[aNode]:
            vertices = np.array([[0, aNode],[0+PlotConsts.XSep, aNeighbor]])
            plot(vertices[:, 0], vertices[:, 1], color = 'g')
            #print vertices
    ymin, ymax = ylim()   # return the current ylim
    ylim(-1, ymax)
    show()


        
def plotFromLists(nodesA, nodesB, adjListA, minMatchLen = 0,\
                      dispIntersPairs=False):
    nodesACoord = coordsConverter.getCoordinatesDict(nodesA)
    nodesBCoord = coordsConverter.getCoordinatesDict(nodesB)
    #print adjListA
    #print nodesA
    #print nodesACoord
    #print nodesB
    #print nodesBCoord
    print 'made nodesACoord, nodesBCoord', len(nodesACoord), len(nodesBCoord)
    sys.stdout.flush()
    intersectionCount, numLines, intersectingPairs\
        = coordsConverter.getIntersectionCount(nodesA,\
                                                   nodesACoord,\
                                                   nodesBCoord,\
                                                   adjListA,\
                                                   dispIntersPairs)
    print 'plotFromLists: Intersection count: ',  intersectionCount
    print 'plotFromLists: Num lines: ',  numLines
    if dispIntersPairs:
        print 'Intersecting pairs:', intersectingPairs
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
            #print vertices
    ymin, ymax = ylim()   # return the current ylim
    ylim(0, ymax)
    show()
    
