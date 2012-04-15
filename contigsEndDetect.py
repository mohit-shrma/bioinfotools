import sys

"""from mummer output based on start and end pts, identify the contigs that
overlapped at end append 'S/E/SF/EF' if yes and '0' other wise"""


def detectIfEndAlign(ipFileName, outFileName):
    #matched start and end columns of query and reference
    #TODO: check if last index is length - 1 in base
    queryMatchStartCol = 3
    queryMatchEndCol = 4
    queryLengthCol = 9
    
    refMatchStartCol = 1
    refMatchEndCol = 2
    refLengthCol = 8
    
    ipFile = open(ipFileName, 'r')
    opFile = open(outFileName, 'w')
    if ipFile and opFile:
        for line in ipFile:
            line = line.rstrip('\n')
            lineStrs = line.split()
            #get start and end, -1 as zero indexing
            queryMatchStart = int(lineStrs[queryMatchStartCol-1])
            queryMatchEnd = int(lineStrs[queryMatchEndCol-1])
            queryLength = int(lineStrs[queryLengthCol - 1])
            
            refMatchStart = int(lineStrs[refMatchStartCol - 1])
            refMatchEnd = int(lineStrs[refMatchEndCol - 1])
            refLength = int(lineStrs[refLengthCol - 1])

            queryEndRefStartOvrlap = False
            queryStartRefEndOvrlap = False
            queryStartRefStartFlipped = False
            queryEndRefEndFlipped = False
            
            #identify if query end overlaps reference start
            if queryMatchEnd == (queryLength) and refMatchStart == 1:#0
                #query end and reference start overlaps
                queryEndRefStartOvrlap = True
                
            #identify if reference end overlaps query start
            if queryMatchStart == 1 and refMatchEnd == (refLength):
                #query end and reference start overlaps
                queryStartRefEndOvrlap = True
            
            if queryMatchEnd == 1 and refMatchStart == 1:
                #query start and reference start overlaps with flipped query
                queryStartRefStartFlipped = True

            if queryMatchStart == queryLength and refMatchEnd == refLength:
                #query end and reference end overlaps with flipped query
                queryEndRefEndFlipped = True

            endOverlapType='0'
            if queryEndRefStartOvrlap:
                endOverlapType='S'
            if queryStartRefEndOvrlap:
                endOverlapType='E'
            if queryStartRefStartFlipped:
                endOverlapType = 'SF'
            if queryEndRefEndFlipped:
                endOverlapType = 'EF'

            lineStrs.append(endOverlapType)
            line = '\t'.join(lineStrs)
            
            opFile.write(line)
            opFile.write('\n')


def main():
    if len(sys.argv) >= 3:
        ipFile = sys.argv[1]
        opFile = sys.argv[2]
        detectIfEndAlign(ipFile, opFile)
    else:
        print 'err: files missing'


if __name__ == '__main__':
    main()
