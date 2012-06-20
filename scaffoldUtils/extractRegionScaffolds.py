import sys
import os

def displayScaff(start, end, fastaFileName):
    with open(fastaFileName, 'r') as fastaFile:
        header = fastaFile.readline()
        fastaStr = fastaFile.readline().rstrip('\n')
        print '>' + os.path.basename(fastaFileName) + '_' + str(start)\
            + '_' + str(end)
        print fastaStr[start-1:end]

def main():
    argLen = len(sys.argv)
    if argLen >=4:
        fastaFileName = sys.argv[1]
        start = int(sys.argv[2])
        end = int(sys.argv[3])
        displayScaff(start, end, fastaFileName)
    else:
        print 'err: less num of args passed'


if __name__ == '__main__':
    main()
