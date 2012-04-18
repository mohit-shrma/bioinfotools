"""this extract matching region detected by mummer-suffix tree algo,
passed file containing contigs name start and ending matching regions,
fasta file containing desired contigs,
output file to whixh to write matched regions"""

import sys

""" matching dict -> 'contigs name'-> {'start': x, 'end':y}"""
def extractMatchedRegion(matchingDict, contigsFastaFileName, opFileName):
    try:
        contigsFile = open(contigsFastaFileName, 'r')
        opFile = open(opFileName, 'w')
        line=contigsFile.readline()
        while line:
            if line.startswith('>'):
                #detected header
                header = line.lstrip('>').rstrip('\n').split()[0]
                if header in matchingDict:
                    #current contig one of matching contig
                    #extract the matching region from it
                    start = matchingDict[header][0] - 1
                    end = matchingDict[header][1] - 1
                    if end < start:
                        #contigs matching in reverse direction
                        start, end = end, start
                    contigs = contigsFile.readline().rstrip('\n')
                    matched = contigs[start:end+1]
                    opFile.write('>')
                    opFile.write(header)
                    opFile.write('\n')
                    opFile.write(matched)
                    opFile.write('\n')                    
                    #don't need this key, can delete it
                    del matchingDict[header]
                    if len(matchingDict) == 0:
                        #all the dict is processed exit the loop
                        break
            line = contigsFile.readline()
        contigsFile.close()
        opFile.close()
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)


""" returns a matching dictionary containg positions of all matched regions"""
def createMatchingDict(matchFileName):
    matchingDict = {}
    headerColNo = 1 -1 #-1 as zero based indexing
    startColNo = 2 -1
    endColNo = 3 -1
    try:
        matchFile = open(matchFileName, 'r')
        header = matchFile.readline()
        for line in matchFile:
            columns = line.split()
            header = columns[headerColNo]
            start = columns[startColNo]
            end = columns[endColNo]
            matchingDict[header] = [int(start), int(end)]
        matchFile.close()
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)
    return matchingDict

def batchExtractMatchingRegion(matchingDict, contigsFileName, opFile):
    try:
        contigsFile = open(contigsFastaFileName, 'r')
        line=contigsFile.readline()
        while line:
            if line.startswith('>'):
                #detected header
                header = line.lstrip('>').rstrip('\n').split()[0]
                if header in matchingDict:
                    #current contig one of matching contig
                    #extract the matching region from it
                    start = matchingDict[header][0]
                    end = matchingDict[header][1]
                    if end < start:
                        #contigs matching in reverse direction
                        start, end = end, start
                    contigs = contigsFile.readline().rstrip('\n')
                    matched = contigs[start:end+1]
                    opFile.write('>')
                    opFile.write(header)
                    opFile.write('\n')
                    opFile.write(matched)
                    opFile.write('\n')
                    opFile.flush()
                    #don't need this key, can delete it
                    del matchingDict[header]
                    if len(matchingDict) == 0:
                        #all the batch is processed exit the loop
                        break
            line = contigsFile.readline()
        contigsFile.close()
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)



""" huge file so lets do batch extraction"""
def doBatchExtraction(matchFileName, contigsFileName, opFileName):
    matchingDict = {}
    headerColNo = 1 -1 #-1 as zero based indexing
    startColNo = 2 -1
    endColNo = 3 -1
    #size of dict to be created at one time and send fwd for processing
    batchLength = 1000 
    try:
        matchFile = open(matchFileName, 'r')
        opFile = open(opFileName, 'w')
        header = matchFile.readline()
        for line in matchFile:
            columns = line.split()
            header = columns[headerColNo]
            start = columns[startColNo]
            end = columns[endColNo]
            matchingDict[header] = [int(start), int(end)]
            if len(matchingDict) >= batchLength:
                #process these batch and empty the dict
                batchExtractMatchingRegion(matchingDict, contigsFileName, opFile)
                #empty the dict
                matchingDict = {}
        matchFile.close()
        opFileName.close()
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)


def main():
    if len(sys.argv) >= 3:
        matchedFileName = sys.argv[1]
        contigsFileName = sys.argv[2]
        opFileName = sys.argv[3]
        matchingDict = createMatchingDict(matchedFileName)
        extractMatchedRegion(matchingDict, contigsFileName, opFileName)
    else:
        print 'err: files missing'

if __name__ == '__main__':
    main()


