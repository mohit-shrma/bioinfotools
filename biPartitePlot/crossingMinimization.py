""" compute order that minimizes cross in bipartite graph by applying mean
heuristics"""

import operator
import math
import graphUtil


#compute the order based on rank of neighbor
def orderByBarycenterHeuristics(nodesList, nodesAdjacencyList,\
                                    neighborRankDict):
    #hold new calculated nodes rank
    nodesRank = {}
    for node in nodesList:
        neighborsRankSum = 0
        for neighbor in nodesAdjacencyList[node]:
            neighborsRankSum += neighborRankDict[neighbor]
        numNeighbors = len(nodesAdjacencyList[node])
        if numNeighbors > 0:
            nodesRank[node] = (float(neighborsRankSum)/numNeighbors)
        else:
            nodesRank[node] = 0
    nodeRankTuples = [(node, nodesRank[node]) for node in nodesList]
    #sort according to nodes rank
    nodeRankTuples = sorted(nodeRankTuples, key=lambda node: node[1])
    newNodesOrder = [ name for name, rank in nodeRankTuples]
    return newNodesOrder



def orderByBarycenterHeuristics2(nodeAdjList):

    #hold new nodes rank (indice, rank)
    nodesRank = []

    for node in range(len(nodeAdjList)):
        neighborRankSum = 0
        for neighbor in nodeAdjList[node]:
            neighborRankSum += neighbor
        numNeighbors = len(nodeAdjList[node])
        if numNeighbors > 0:
            nodesRank.append(\
                (node, math.floor(float(neighborRankSum)/numNeighbors)))
        else:
            nodesRank.append((node, 0))

    #now order nodes in nodeAdjList according to nodesRank
    nodesRank.sort(key=operator.itemgetter(1))

    #newIndices[originalNodeIndice] -> newNodeIndice
    newIndices = range(len(nodeAdjList))
    for newInd in  range(len(nodesRank)):
        origInd, rank = nodesRank[newInd]
        newIndices[origInd] = newInd
    
    newNodeAdjList = [ nodeAdjList[origInd] for origInd, rank in nodesRank] 

    return newIndices, newNodeAdjList

#modify passed adj list in-place to update with values from new neighbors indices
def updateAdjList(newNeighborIndices, oldAdjList):
    for i in range(len(oldAdjList)):
        neighbors = oldAdjList[i]
        for j in range(len(neighbors)):
            neighbors[j] = newNeighborIndices[neighbors[j]]
    return oldAdjList

    
#return a rank dictionary based on given node list, basically indices
#associated with name
def prepareRankDict(nodesList, rankDict):
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



def applyBarycenterHeuristics2(nodeAdjList):

    #get new order by applying heuristics
    newIndices, newNodeAdjList = orderByBarycenterHeuristics2(nodeAdjList)
    
    #check if order same as old or not
    for i in range(len(newIndices)):
        if i != newIndices[i]:
            return newIndices, newNodeAdjList, True
    return newIndices, newNodeAdjList, False


def minimumCrossingOrdering2(refAdjList, queryAdjList):
    positionChanged = True
    counter = 1 

    while positionChanged:
        positionChanged = False
        if counter%2 == 0:
            #choose refAdjList to play
            newRefIndices, newNodeAdjList, positionChanged\
                = applyBarycenterHeuristics2(refAdjList)
            #assign new adjlist to refadjlist
            refAdjList = newNodeAdjList
            #update query adj list with new refInd
            queryAdjList = updateAdjList(newRefIndices, queryAdjList)
        else:
            #choose queryAdjList to play
            newQueryIndices, newNodeAdjList, positionChanged\
                = applyBarycenterHeuristics2(queryAdjList)
            #assign new adjlist to queryadjlist
            queryAdjList = newNodeAdjList
            #update ref adj list with new queryInd
            refAdjList = updateAdjList(newQueryIndices, refAdjList)
        counter += 1
    return refAdjList, queryAdjList



#find order lists as per connected components list
def getOrderedLists(connectedRefs, refAdjList, queryAdjList):
    refList = []
    queryList = []
    for connectedComp in connectedRefs:
        for refNode in connectedComp:
            refList.append(refNode)
            for queryNode in set(refAdjList[refNode]):
                if queryNode not in queryList:
                    queryList.append(queryNode)

    if len( set(refAdjList.keys()) ^ set(refList) ) > 0 or\
            len( set(queryAdjList.keys()) ^ set(queryList) ) > 0:
            print 'err: missing some nodes either in ref or query'
            return [],[]

    return refList, queryList



#return order of both ref and query minimizing crossings in between
#passed adjacncy list as dict, node -> [nodeNeighbor1, ...]    
def minimumCrossingOrdering(refAdjList, queryAdjList):

    #get connected components cluster
    connectedRefs = graphUtil.findConnectedComps(refAdjList, queryAdjList)

    #use connected comps to decide the initial order
    refNodes, queryNodes = getOrderedLists(connectedRefs, refAdjList,\
                                               queryAdjList)
    
    print 'refNodes b4 cross min: ', refNodes
    print 'queryNodes b4 cross min: ', queryNodes
    
    #apply barycenter heuristices alternately on ref then query until their
    #position remains same in order
    positionChanged = True
    counter = 0

    #initialize query Rank Dict
    queryRankDict = {}

    #initialize ref Rank Dict
    refRankDict = {}
    while positionChanged:
        positionChanged = False
        if counter%2 == 0:
            #choose ref nodes to play around
            queryRankDict = prepareRankDict(queryNodes, queryRankDict)
            refNodes, positionChanged = applyBarycenterHeuristics(refNodes,\
                                                                      refAdjList,\
                                                                      queryRankDict)
        else:
            #choose query nodes to play around
            refRankDict = prepareRankDict(refNodes, refRankDict)
            queryNodes, positionChanged = applyBarycenterHeuristics(queryNodes,\
                                                                        queryAdjList,\
                                                                        refRankDict)
        counter += 1
    return refNodes, queryNodes

    
