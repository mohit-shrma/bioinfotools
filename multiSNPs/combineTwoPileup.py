import sys
import os 
import csv


class PILEUP_CONSTS:

    SCAFF_COL = 0
    BASE_POS_COL = 1
    COUNT_COL = 3
    FILTR_PRE = 'filtered_'



class FILTR_PILEUP_CONSTS:
    SCAFF_COL = 0
    BASE_POS_COL = 1
    COUNT_COL = 2


def getScaffPosCount(row):
    scaff = row[PILEUP_CONSTS.SCAFF_COL]
    pos = row[PILEUP_CONSTS.BASE_POS_COL]
    count = row[PILEUP_CONSTS.COUNT_COL]
    return (scaff, pos, count)


def getScaffsets(scaffListFileName):
    scaffSets = set([])
    with open(scaffListFileName, 'r') as scaffListFile:
        for line in scaffListFile:
            scaffSets.add(line.strip())
    return scaffSets


def getIntsum(pileupFileName, step, opFileName, scaffSets):
    with open(pileupFileName, 'r') as pileupFile,\
            open(opFileName, 'w') as opFile:

        pileupReader = csv.reader(pileupFile)
        prevScaffName = ''

        iter = 1
        sum = 0
        currBasePos = 0
        currStepStartBase = 0

        for row in pileupReader:
            
            (pileupScaff, pileupPos, pileupCount) = \
                getScaffPosCount(row)

            if pileupScaff not in scaffSets:
                continue

            if pileupScaff != prevScaffName and prevScaffName != '':
                #display last sum and scaff pos
                opFile.write('\t'.join([prevScaffName, str(pileupPos),\
                                            str(pileupCount),\
                                            str(currStepStartBase,\
                                                    str(sum))]) + '\n')
                #found new scaff
                currStepStartBase = 0
                iter = 1
                sum = 0
                prevScaffName = pileupScaff

            if pileupPos > step*iter:
                #display new scaff
                opFile.write('\t'.join([prevScaffName, str(pileupPos),\
                                            str(pileupCount),\
                                            str(currStepStartBase),\
                                            str(sum)]) + '\n')
                currStepStartBase = untilPos + 1
                iter = 2
                sum = 0
            
            sum += pileupCount

        #print the last pending sums
        opFile.write('\t'.join([prevScaffName, str(pileupPos),\
                                            str(pileupCount),\
                                            str(currStepStartBase),\
                                            str(sum)]) + '\n')


def main():
    if len(sys.argv) > 4:
        pileupFileName = sys.argv[1]
        opFileName = sys.argv[2]
        step = sys.argv[3]
        scaffListName = sys.argv[4]
        scaffSets = getScaffsets(scaffListFileName)
        getIntsum(pileupFileName, step, opFileName, scaffSets)
    else:
        print err
  
                
            
if __name__=='__main__':
    main()
