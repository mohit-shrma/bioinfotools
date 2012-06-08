

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
        refY += 100
        
    #add query nodes
    for queryNode in queryNodesOrdered:
        allNodes.append(getNodeString(queryNode, queryNode, queryX, queryY, 'query'))
        queryY += 100
    return '\n'.join(allNodes)



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
