
#apply BFS to find the connected components in graph
#returns nodes which cluster together in ref, they can be used to know query
def findConnectedComps(refAdjList, queryAdjList):
    refNodes = refAdjList.keys()
    connectedRefComps = []
    while len(refNodes) > 0:
        #till all the reference nodes are done

        #pull out a node from reference list to do process
        refNode = refNodes.pop(0)

        currentRefNodeQ = []

        currentRefComps = []

        #add to q the current refNode
        currentRefNodeQ.append(refNode)

        while len(currentRefNodeQ) > 0:
            poppedRef = currentRefNodeQ.pop(0)
            #for each query node connected to poppedRef, 
            #process also the refnodes connected to them
            for queryNode in set(refAdjList[poppedRef]):
                #find all refnode connected to queryNode barring refNode
                for refNeighbor in set(queryAdjList[queryNode]):
                    if refNeighbor != poppedRef and\
                            refNeighbor not in currentRefComps and\
                            refNeighbor not in currentRefNodeQ and\
                            refNeighbor in refNodes:
                        currentRefNodeQ.append(refNeighbor)
            currentRefComps.append(poppedRef)

        connectedRefComps.append(currentRefComps)
        
        #remove ref nodes in currently connected components from refNodes
        for node in currentRefComps:
            if node in refNodes:
                refNodes.remove(node)
                
    return connectedRefComps


#return ref nodes, query nodes, ref adj list
#for the passed ref nodes
def getClusterComps(refNodes, refAdjList, queryAdjList):
    queryNodes = []
    subRefAdjList = {}
    subQueryAdjList = {}
    for refNode in refNodes:
        subRefAdjList[refNode] = refAdjList[refNode]
        for queryNode in refAdjList[refNode]:
            queryNodes.append(queryNode)
            subQueryAdjList[queryNode] = queryAdjList[queryNode]
    return refNodes , list(set(queryNodes)), subRefAdjList, subQueryAdjList
