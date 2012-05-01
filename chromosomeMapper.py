""" maps bgi scaffold chromosome dict from a file to other i.e. NCGR scaffolds """
import sys


def getBgiScaffoldChromDict(dictFileName):
    scaffNameCol = 1 - 1
    chromCol = 2 - 1
    try:
        dictFile = open(dictFileName, 'r')
        header = dictFile.readline()
        chromDict = {}
        for line in dictFile:
            line = line.rstrip('\n').split()
            scaffName = line[scaffNameCol]
            chromName = line[chromCol]
            chromDict[scaffName] = chromName
        dictFile.close()
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)        
    return chromDict

def findNCGRChrom(ncgrBgiMapFileName, bgiChromDict):
    #ncgr scaffold name
    ncgrScaffNameCol = 1 - 1
    #comma separated list of bgi scaffolds mapping to ncgr scaffold
    matchedBgiScaffsCol = 2 - 1
    try:
        ncgrBgiFile = open(ncgrBgiMapFileName, 'r')
        header = ncgrBgiFile.readline()
        print 'scaffName', 'chromosomes'
        for line in ncgrBgiFile:
            line = line.rstrip('\n').split()
            ncgrScaffName = line[ncgrScaffNameCol]
            bgiScaffs = line[matchedBgiScaffsCol].split(',')
            chromsMapped = ''
            for bgiScaff in bgiScaffs:
                if bgiScaff in bgiChromDict:
                    chromsMapped += bgiChromDict[bgiScaff]+','
            chromsMapped = chromsMapped.rstrip(',')
            if len(chromsMapped) > 0:
                print ncgrScaffName, chromsMapped
        ncgrBgiFile.close()
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)        
    

        
def main():
    if len(sys.argv) >= 2:
        bgiScaffoldDictFileName = sys.argv[1]
        bgi2NCGRFileName = sys.argv[2]
        bgiChromDict = getBgiScaffoldChromDict(bgiScaffoldDictFileName)
        findNCGRChrom(bgi2NCGRFileName, bgiChromDict)
    else:
        print 'err: files missing'

if __name__ == '__main__':
    main()

