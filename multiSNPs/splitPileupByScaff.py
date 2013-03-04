import sys
import os
import csv


class Pileup_Consts:
    SCAFF_NAME = 0
    BASE_POS = 1
    COUNT = 3



def splitByScaff(pileUpFileName, opDir):
    with open(pileUpFileName, 'r') as pileUpFile:
        pileUpReader = csv.reader(pileUpFile, delimiter='\t')
        prevScaffName = ''
        currScaffFile = None
        currScaffWriter = None
        for row in pileUpReader:
            scaffName = row[Pileup_Consts.SCAFF_NAME]
            if prevScaffName == scaffName:
                #continue to write in current scaff file
                currScaffWriter.writerow(row)
            else:
                #found a new scaff, close old file
                currScaffFile.close()
                #open and write new file
                currScaffFile = open(\
                    os.path.join(opDir, scaffName + '.mpileup'), 'w')
                currScaffWriter = csv.writer(pileUpFile, delimiter='\t')
                currScaffWriter.writerow(row)
                prevScaffName = scaffName


def main():
    if len(sys.argv) > 3:
        pileUpFileName = os.path.abspath(sys.argv[1])
        opDir = os.path.abspath(sys.argv[2])
        splitByScaff(pileUpFileName, opDir)
    else:
        print 'err: invalid args'
        

if __name__ == '__main__':
    main()
