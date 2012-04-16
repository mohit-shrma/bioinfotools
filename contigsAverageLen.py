import sys

"""calculate average contigs length in file"""

def getAvgLen(ipFileName):
    totalLen = 0
    numContigs = 0
    try:
        file = open(ipFileName, 'r')
        for line in file:
            if not line.startswith('>'):
                totalLen += len(line.rstrip('\n'))
            else:
                numContigs += 1
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)        
    if numContigs > 0:
        return totalLen, numContigs, totalLen/numContigs
    else:
        return totalLen, numContigs, 0


def main():
    if len(sys.argv) >= 1:
        ipFileName = sys.argv[1]
        print 'total length, num contigs, average contigs length', \
            getAvgLen(ipFileName)
    else:
        print 'err: files missing'

if __name__ == '__main__':
    main()
