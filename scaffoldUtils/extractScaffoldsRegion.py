import sys
import os
import csv

class REGIONS_FILE:
    SCAFF_COL = 2
    START_COL = 3
    END_COL = 4


#assuming scaffold in extract regions are in sorted order
def  extractRegions(scaffoldsFileName, regionsFileName, outputFileName,\
                       delim='\t', zeroStart=False):
    with open(scaffoldsFileName, 'r') as scaffoldsFile, \
            open(regionsFileName, 'r') as regionsFile, \
            open(outputFileName, 'w') as outputFile:

        regionsFileReader = csv.reader(regionsFile, delimiter=delim)
        
        currScaffName = ''
        currScaffseq =''
        
        for row in regionsFileReader:
            scaffName = row[REGIONS_FILE.SCAFF_COL]
            start = int(row[REGIONS_FILE.START_COL])
            end = int(row[REGIONS_FILE.END_COL])

            while (currScaffName != scaffName):
                #read scaffolds from file
                currScaffName = scaffoldsFile.readline().strip().lstrip('>')
                currScaffseq = scaffoldsFile.readline().strip()

            if zeroStart:
                #TODO: confirm this 
                extractedReg = currScaffseq[start:end+1]
            else:
                extractedReg = currScaffseq[start-1:end]

            outputFile.write('>' + currScaffName + '_' + str(start) + '_'\
                                 + str(end) + '\n')
            outputFile.write(extractedReg);
            outputFile.write('\n')
            


def main():

    if len(sys.argv) > 3:
        regionsFileName = sys.argv[1]
        scaffoldsFileName = sys.argv[2]
        outputFileName = sys.argv[3]
        extractRegions(scaffoldsFileName, regionsFileName, outputFileName)
    else:
        print 'err: invalid args'


if __name__=='__main__':
    main()
