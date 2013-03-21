import sys
import csv
import os



def splitByScaff(ipFileName, opDir, scaffColInd, delim=None):

    with open(ipFileName, 'r') as ipFile:
        ipFileReader =csv.reader(ipFile, delimiter=delim)
        prevScaffName = ''
        scaffFile = None
        scaffFileWriter = None
        fileExt = ipFileName.split('.')[-1]
        for row in ipFileReader:
            scaffName = row[scaffColInd]
            if prevScaffName != scaffName:
                #close prev file
                if scaffFile is not None:
                    scaffFile.close()
                #open new file
                scaffFile = open(\
                    os.path.join(opDir, scaffName + '.' + fileExt), 'w')
                scaffFileWriter = csv.writer(scaffFile, delimiter=delim)
            scaffFileWriter.writerow(row)
                


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
