import sys
import csv
import os



def splitByScaff(ipFileName, opDir, scaffColInd, delim=None):

    with open(ipFileName, 'r') as ipFile:
        ipFileReader =csv.reader(ipFile, delimiter=delim)
        prevScaffName = ''
        scaffFile = None
        scaffFileWriter = None
        scaffDirPath = None
        fileExt = ipFileName.split('.')[-1]
        for row in ipFileReader:
            scaffName = row[scaffColInd]
            if prevScaffName != scaffName:
                #close prev file
                if scaffFile is not None:
                    scaffFile.close()
                #create new dir
                scaffDirPath = os.path.join(opDir, scaffName)
                if not os.path.isdir(scaffDirPath):
                    os.mkdir(scaffDirPath)
                #open new file
                scaffFile = open(\
                    os.path.join(scaffDirPath, scaffName + '.' + fileExt), 'w')
                prevScaffName = scaffName
            scaffFile.write('\t'.join(row) + '\n')
                


def main():
    if len(sys.argv) > 3:
        ipFileName = sys.argv[1]
        opDir = sys.argv[2]
        scaffColInd = int(sys.argv[3])
        splitByScaff(ipFileName, opDir, scaffColInd, delim='\t')
    else:
        print 'err: invalid arguments'



if __name__ == '__main__':
    main()
