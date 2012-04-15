import sys

"""from mummer output based on start and end pts, identify the contigs that
overlapped at end append '1' if yes and '0' other wise"""


def detectIfEndAlign(ipFileName, outFileName):
    #matched start and end columns of query and reference
    #TODO: check if last index is length - 1 in base
    queryStartCol = 3
    queryEndCol = 4
    queryLengthCol = 9
    
    refStartCol = 1
    refEndCol = 2
    refLengthCol = 8
    
    ipFile = open(ipFileName, 'r')
    opFile = open(outFileName, 'w')
    if ipFile and opFile:
        for line in ipFile:
            line = line.rstrip('\n')
            lineStrs = line.split()
            #get start and end, -1 as zero indexing
            queryStart = int(lineStrs[queryStartCol-1])
            queryEnd = int(lineStrs[queryEndCol-1])
            queryLength = int(lineStrs[queryLengthCol - 1])
            
            refStart = int(lineStrs[refStartCol - 1])
            refEnd = int(lineStrs[refStartCol - 1])
            refLength = int(lineStrs[refLengthCol - 1])

            queryEndRefStartOvrlap = False
            queryStartRefEndOvrlap = False
            #identify if query end overlaps reference start
            #TODO: queryLength - 1 check
            if queryEnd == (queryLength) and refStart == 1:#0
                #query end and reference start overlaps
                queryEndRefStartOvrlap = True
            #identify if reference end overlaps query start
            #TODO: refLength - 1 check
            if queryStart == 1 and refEnd == (refLength):
                #query end and reference start overlaps
                queryStartRefEndOvrlap = True
            endOverlapType='0'
            if queryEndRefStartOvrlap:
                endOverlapType='S'
            if queryStartRefEndOvrlap:
                endOverlapType='E'
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
