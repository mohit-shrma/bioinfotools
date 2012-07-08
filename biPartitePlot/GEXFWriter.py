#class  to hold constant specific to graph layout,  won't be change while execution 
class GEXFWriterConstants:
    #distance between left/ref and right/query nodes
    REF_QUERY_DIST = 500

    #distance between two separate blocks of left/right nodes
    REF_QUERY_BLOCK_DIST = 500

    #vertical distance between two y nodes
    Y_OFFSET = 100

    #MAX Y OFFSET
    MAX_Y_OFFSET = 45000
    
def getGexfHeader():
    return """<?xml version="1.0" encoding="UTF-8"?>\n<gexf xmlns="http://www.gexf.net/1.2draft" xmlns:viz="http://www.gexf.net/1.2draft/viz" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.gexf.net/1.2draft http://www.gexf.net/1.2draft/gexf.xsd" version="1.2">"""


def getNodeString(nodeLabel, nodeId, x, y, classType=''):
    return "<node id=\""+ nodeId + "\" label=\"" + nodeLabel +"\">\n"\
        + '<viz:position x="' + str(x) +'" y="' + str(y) +'" z="0.0"/>'\
        + "<attvalues>\n<attvalue for=\"0\" value=\"" + classType + "\"/>\n</attvalues>"\
        + "\n</node>"


def getEdgeString(edgeId, sourceId, targetId):
    return "<edge id=\""+ edgeId + "\" source=\"" + sourceId\
        + "\" target=\"" + targetId + "\" />"


def getAllEdgesString(refNodesOrdered, refAdjList):
    allEdges = []
    for node in refNodesOrdered:
        for neighbor in set(refAdjList[node]):
            allEdges.append(getEdgeString(node+':'+neighbor, node, neighbor))
    return '\n'.join(allEdges)



def getAllNodesString(refNodesOrdered, queryNodesOrdered):
    allNodes = []
    refX = 0
    refY = 0
    queryX = 800
    queryY = 0
    #add reference nodes
    for refNode in refNodesOrdered:
        allNodes.append(getNodeString(refNode, refNode, refX, refY, 'ref'))
        refY += GEXFWriterConstants.Y_OFFSET
        
    #add query nodes
    for queryNode in queryNodesOrdered:
        allNodes.append(getNodeString(queryNode, queryNode, queryX, queryY, 'query'))
        queryY += GEXFWriterConstants.Y_OFFSET
            
    return '\n'.join(allNodes)


def getYnClusterString(nodeCluster, refX, refY, queryX, queryY):
    clusterNodes = []
    [refOrderList, queryOrderList, intersectionCount] = nodeCluster

    #add ref nodes
    for refNode in refOrderList:
        clusterNodes.append(getNodeString(refNode, refNode, refX, refY, 'ref'))
        refY += GEXFWriterConstants.Y_OFFSET

    #add query nodes
    for queryNode in queryOrderList:
        clusterNodes.append(getNodeString(queryNode, queryNode, queryX, queryY, 'query'))
        queryY += GEXFWriterConstants.Y_OFFSET

    return refY, queryY, '\n'.join(clusterNodes)
        
        
#generate node string from passed clusters
#care should be taken to draw full cluster as block and if it exceeds the margin then
#it should be relayout to the right again
def getAllNodesStringFromCluster(nodeClusters):
    allNodes = []

    refX = 0
    refY = 0
    
    queryX = refX + GEXFWriterConstants.REF_QUERY_DIST
    queryY = 0
    
    for  nodeCluster in nodeClusters:
        #lay out refnodes of cluster
        refY, queryY, clusterNodesString = getYnClusterString(nodeCluster,\
                                                                  refX, refY,\
                                                                  queryX, queryY)
        if refY > GEXFWriterConstants.MAX_Y_OFFSET \
                or queryY > GEXFWriterConstants.MAX_Y_OFFSET:
            #either Y exceeds max offset limit
            #reset refY, refX, queryY, queryX to new block location
            refX = refX + GEXFWriterConstants.REF_QUERY_DIST + \
                GEXFWriterConstants.REF_QUERY_BLOCK_DIST
            refY = 0

            queryX = refX + GEXFWriterConstants.REF_QUERY_DIST
            queryY = 0

            #relayout cluster with new coordinates
            refY, queryY, clusterNodesString = getYnClusterString(nodeCluster,\
                                                                      refX, refY,\
                                                                      queryX, queryY)
        allNodes.append(clusterNodesString)
    
    return '\n'.join(allNodes)        

        
    

#generate GEF xml formatted string for passed adjacency list and cluster of nodes
# node cluster is a list of format refOrerList, queryOrderList, intersectionCount
# [[refOrderList, queryOrderList, intersectionCount],...]
def getGexfXMLStringFromCluster(refAdjList, nodeClusters):
    xmlStrList = []

    #getHeader
    xmlStrList.append(getGexfHeader())

    #add graph header
    xmlStrList.append('<graph>')

    #add attribute
    xmlStrList.append('<attributes class="node">\n'\
                          +'<attribute id="0" title="class" type="string"/>\n'\
                          +'\n</attributes>')

    
    #add nodes header
    xmlStrList.append('<nodes>')

    #add all nodes
    xmlStrList.append(getAllNodesStringFromCluster(nodeClusters))
    
    #add nodes tail
    xmlStrList.append('</nodes>')

    #add edges header
    xmlStrList.append('<edges>')

    refList = []
    for orderCluster in nodeClusters:
        refList += orderCluster[0]
    
    #add all edges
    xmlStrList.append(getAllEdgesString(refList, refAdjList))

    #add edges tail
    xmlStrList.append('</edges>')
    
    #add graph tail
    xmlStrList.append('</graph>')
    
    #getTail
    xmlStrList.append('</gexf>\n')

    return '\n'.join(xmlStrList)


def getGexfXMLString(refAdjLst, refNodesOrdered, queryNodesOrdered):
    xmlStrList = []

    #getHeader
    xmlStrList.append(getGexfHeader())

    #add graph header
    xmlStrList.append('<graph>')

    #add attribute
    xmlStrList.append('<attributes class="node">\n'\
                          +'<attribute id="0" title="class" type="string"/>\n'\
                          +'\n</attributes>')

    
    #add nodes header
    xmlStrList.append('<nodes>')

    #add all nodes
    xmlStrList.append(getAllNodesString(refNodesOrdered, queryNodesOrdered))
    
    #add nodes tail
    xmlStrList.append('</nodes>')

    #add edges header
    xmlStrList.append('<edges>')

    #add all edges
    xmlStrList.append(getAllEdgesString(refNodesOrdered, refAdjLst))

    #add edges tail
    xmlStrList.append('</edges>')
    
    #add graph tail
    xmlStrList.append('</graph>')
    
    #getTail
    xmlStrList.append('</gexf>\n')

    return '\n'.join(xmlStrList)
