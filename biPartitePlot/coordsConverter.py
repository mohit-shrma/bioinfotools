""" following converts to coordinates, so that can be plotted"""
import math

def getCoordinatesDict(nodesList):
    sepDist = 2
    prevEnd = 0
    cordDict = {}
    for node in nodesList:
        start = prevEnd + 1
        end = start + sepDist - 1
        cordDict[node] = [start, end]
        prevEnd = end
    return cordDict


#intersection of two lines given their end y's
#(y1,y2) are y's of one line endpoint ||ly (y3, y4)
def isIntersect(y1, y2, y3, y4):
    diff1 = y1- y3
    diff2 = y2 - y4
    if (diff1*diff2) >= 0:
        #print 'not intersect: ', y1, y2, y3, y4
        return False
    else:
        #print 'intersect: ', y1, y2, y3, y4
        return True


    
def getIntersectionCountFromAdj(adjListA):
    intersectionCount = 0
    numLines = 0
    for aNode in range(len(adjListA)):
        for aNodeNeighbor in adjListA[aNode]:
            #check for intersection of line (aNode, aNodeNeighbor)
            #end y coords of line
            y1 = aNode
            y2 = aNodeNeighbor
            numLines += 1
            for otherNode in range(aNode+1, len(adjListA)):
                for otherNeighbor in adjListA[otherNode]:
                    #other line is (othernode, otherneighbor)
                    y3 = otherNode
                    y4 = otherNeighbor
                    if isIntersect(y1, y2, y3, y4):
                        intersectionCount += 1
    return intersectionCount, numLines
    
def getIntersectionCount(nodesAList, nodesACoord,\
                             nodesBCoord, nodesAAdjList):
    intersectionCount = 0
    numLines  = 0
    #intersectingPairs = []
    for i in range(len(nodesAList)):
        currNode = nodesAList[i]
        for currNeighbor in nodesAAdjList[currNode]:
            #check for intersection of line (currNode, currNeighbor)
            #end y coords of line
            y1 = math.floor(float(nodesACoord[currNode][0] + nodesACoord[currNode][1])/2)
            y2 = math.floor(float(nodesBCoord[currNeighbor][0]\
                           + nodesBCoord[currNeighbor][1])/2)
            numLines += 1
            #print 'line no. ' + str(numLines) +':', str(y1), ',' , str(y2)
            for j in range(i+1, len(nodesAList)):
                otherNode = nodesAList[j]
                for otherNeighbor in nodesAAdjList[otherNode]:
                    #other line is (otherNode, otherNeighbor)
                    y3 = math.floor(float(nodesACoord[otherNode][0]\
                                   + nodesACoord[otherNode][1])/2)
                    y4 = math.floor(float(nodesBCoord[otherNeighbor][0]\
                                   + nodesBCoord[otherNeighbor][1])/2)
                    if isIntersect(y1, y2, y3, y4):
                        intersectionCount += 1
                        #intersectingPairs.append([(currNode, currNeighbor),\
                        #                              (otherNode, otherNeighbor)])
    return intersectionCount, numLines

    
