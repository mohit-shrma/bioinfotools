import sys
""" validate whether lastz output for X vs Y and Y vs X are same or mutual correspondence"""


def createDict(fileName):
    numNameCol = 0 #1 -1
    numMappedScaffsCol = 4 #5 -1
    origDict = {}
    flippedDict = {}
    try:
        file = open(fileName, 'r')
        header = file.readline()
        for line in file:
            cols = line.rstrip('\n').split('\t')
            name = cols[numNameCol]
            origDict[name] = cols[numMappedScaffsCol]
            scaffs = cols[numMappedScaffsCol].split('|')
            for scaffold in scaffs:
                if scaffold in flippedDict:
                    flippedDict[scaffold] += '|' + name
                else:
                    flippedDict[scaffold] = name
        file.close()
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)
    return origDict, flippedDict
    
def validatFlippedFile(flipedFileName, deduceFlippedDict):
    numNameCol = 0
    numMappedScaffsCol = 4
    missingDict = {}
    try:
        flippedFile = open(flipedFileName, 'r')
        header = flippedFile.readline()
        for line in flippedFile:
            cols = line.rstrip('\n').split('\t')
            name = cols[numNameCol]
            scaffs = cols[numMappedScaffsCol].split('|')
            #from passed dict validate for each scaffs if present there
            if name in deduceFlippedDict:
                mappedScaffs = deduceFlippedDict[name].split('|')
                missedScaffs = []
                for scaffold in scaffs:
                    if scaffold not in mappedScaffs:
                        missedScaffs.append(scaffold)
                if len(missedScaffs) > 0:
                    missingDict[name] = '|'.join(missedScaffs)
            else:
                missingDict[name] = cols[numMappedScaffsCol]
        flippedFile.close()
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)
    return missingDict
                    


def main():
    if len(sys.argv) >= 2:
        queryRefFileName = sys.argv[1]
        queryRefFlippedName = sys.argv[2]
        origDict, flippedDict =  createDict(queryRefFileName)
        missingDict = validatFlippedFile(queryRefFlippedName, flippedDict)
        print 'scaffold'+'\t'+ 'missed mappings'
        for scaffold, missedScaffs in missingDict.iteritems():
            print scaffold + '\t' + missedScaffs
            
    else:
        print 'err: files missing'


if __name__ == '__main__':
    main()
