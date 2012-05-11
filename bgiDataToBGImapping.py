""" takes bgi publish data file and bgi public scaffolds and based on their length try to identify which scaffold corresponds to whic one in data, additionally spits the chromosome mapping info out too"""

import sys

def parseBgiData(bgiFileName):
    scaffNameCol = 1 - 1
    chromosomeCol = 2 - 1
    scaffLengthCol = 3 - 1
    bgiFile = open(bgiFileName, 'r')
    header = bgiFile.readline()
    lengthScaffChromDict = {}
    for line in bgiFile:
        line = line.rstrip('\n').split()
        scaffName = line[scaffNameCol]
        chromosome = line[chromosomeCol]
        scaffLength = line[scaffLengthCol]
        if scaffLength in lengthScaffChromDict:
            lengthScaffChromDict[scaffLength].append(\
                [scaffName, chromosome])
        else:
            lengthScaffChromDict[scaffLength] = [\
                [scaffName, chromosome]]
    return lengthScaffChromDict

def parsePubScaffs(bgiScaffFileName, chromDict):
    scaffNameCol = 1 - 1
    scaffLengthCol = 2 - 1
    bgiScaffFile = open(bgiScaffFileName, 'r')
    header = bgiScaffFile.readline()
    #take out minimum length scaff in dict for termination
    minLength = min(chromDict.keys())
    bgiScaffDict = {}
    for line in bgiScaffFile:
        line = line.rstrip('\n').split()
        scaffLength = line[scaffLengthCol]
        scaffName = line[scaffNameCol]
        if minLength > scaffLength:
            #parsed all necessary scaffolds
            break
        else:
            if scaffLength in chromDict:
                opStr = scaffName +'\t'
                bgiScaffDict[scaffName] = chromDict[scaffLength]
                for scaffChrom in chromDict[scaffLength]:
                    opStr += scaffChrom[0]+'\t'+scaffChrom[1]
                print opStr
    return bgiScaffDict



def main():
    if len(sys.argv) >= 2:
        bgiPaperData = sys.argv[1]
        bgiScaffoldsFile = sys.argv[2]
        chromDict = parseBgiData(bgiPaperData)
        parsePubScaffs(bgiScaffoldsFile, chromDict)
    else:
        print 'err: files missing'

if __name__ == '__main__':
    main()

