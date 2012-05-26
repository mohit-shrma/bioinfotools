""" compute order that minimizes cross in bipartite graph by applying mean
heuristics"""

import operator
import math

#compute the order based on rank of neighbor
def orderByBarycenterHeuristics(nodesList, nodesAdjacencyList,\
                                    neighborRankDict):
    #hold new calculated nodes rank
    nodesRank = {}
    for node in nodesList:
        neighborsRankSum = 0
        for neighbor in nodesAdjacencyList[node]:
            neighborsRankSum += neighborRankDict[neighbor]
        nodesRank[node] = math.floor(\
            float(neighborsRankSum)/len(nodesAdjacencyList[node]))
    #sort according to nodes rank
    sortedNodesRank = sorted(nodesRank.iteritems(), key=operator.itemgetter(1))
    newNodesOrder = [ name for name, rank in sortedNodesRank]
    return newNodesOrder

#return a rank dictionary based on given node list, basically indices
#associated with name
def prepareRankDict(nodesList):
    rankDict = {}
    for i in range(len(nodesList)):
        rankDict[nodesList[i]] = i
    return rankDict

#return true/false depending on whether order changes by applying heuristics
def applyBarycenterHeuristics(origNodesOrder, adjList, neighborRankDict):
    #get new order by applying heuristics
    newNodesOrder = orderByBarycenterHeuristics(origNodesOrder,\
                                                    adjList,\
                                                    neighborRankDict)
    #now check if new order same as previous
    for i in range(len(newNodesOrder)):
        if newNodesOrder[i] != origNodesOrder[i]:
            return newNodesOrder, True
    return newNodesOrder, False
            


#return order of both ref and query minimizing crossings in between
#passed adjacncy list as dict, node -> [nodeNeighbor1, ...]    
def minimumCrossingOrdering(refAdjList, queryAdjList):

    #decides on initial ordering of ref, for now use default random order
    #in which keys might be stored in adjDict
    refNodes = refAdjList.keys()
    queryNodes = queryAdjList.keys()

    #apply barycenter heuristices alternately on ref then query until their
    #position remains same in order
    positionChanged = True
    counter = 0
    while positionChanged:
        positionChanged = False
        if counter%2 == 0:
            #choose ref nodes to play around
            queryRankDict = prepareRankDict(queryNodes)
            refNodes, positionChanged = applyBarycenterHeuristics(refNodes,\
                                                                      refAdjList,\
                                                                      queryRankDict)
        else:
            #choose query nodes to play around
            refRankDict = prepareRankDict(refNodes)
            queryNodes, positionChanged = applyBarycenterHeuristics(queryNodes,\
                                                                        queryAdjList,\
                                                                        refRankDict)
        counter += 1
    return refNodes, queryNodes

    
