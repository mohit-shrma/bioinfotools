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
    return (scaff, int(pos), int(count))


def getScaffsets(scaffListFileName):
    scaffSets = set([])
    with open(scaffListFileName, 'r') as scaffListFile:
        for line in scaffListFile:
            scaffSets.add(line.strip())
    return scaffSets


def getIntsum(pileupFileName, stepCount, opFileName, scaffSets):
    with open(pileupFileName, 'r') as pileupFile,\
            open(opFileName, 'w') as opFile:

        pileupReader = csv.reader(pileupFile, delimiter='\t')
        prevScaffName = ''

        iter = 1
        sum = 0
        currBasePos = 0
        currStepStartBase = 0
        newPileupPos = 0
        newPileupCount = 0
        newPileupScaff = ''

        opFile.write('\t'.join(['scaffold name', 'pileup pos', 'pileup count', 'stepStartBase', 'sum']) + '\n')
        

        for row in pileupReader:
            
            (newPileupScaff, newPileupPos, newPileupCount) = \
                getScaffPosCount(row)

            if newPileupScaff not in scaffSets:
                continue

            if newPileupScaff != prevScaffName:
                #found new scaff
                currStepStartBase = 0
                iter = 1
                sum = 0


                if prevScaffName != '':
                    #display last sum and scaff pos
                    opFile.write('\t'.join([oldPileupScaff, str(oldPileupPos),\
                                                str(oldPileupCount),\
                                                str(currStepStartBase),\
                                                str(sum)]) + '\n')
                prevScaffName = newPileupScaff
                
            if newPileupPos > stepCount*iter:
                #display 
                opFile.write('\t'.join([prevScaffName, str(newPileupPos),\
                                            str(newPileupCount),\
                                            str(currStepStartBase),\
                                            str(sum)]) + '\n')
                currStepStartBase = stepCount*iter + 1
                iter += 1
                sum = 0
            
            sum += int(newPileupCount)
            
            (oldPileupScaff, oldPileupPos, oldPileupCount) = (newPileupScaff, newPileupPos, newPileupCount)
            
        #print the last pending sums
        if newPileupScaff in scaffSets:
            opFile.write('\t'.join([newPileupScaff, str(newPileupPos),\
                                        str(newPileupCount),\
                                        str(currStepStartBase),\
                                        str(sum)]) + '\n')


def main():
    if len(sys.argv) > 4:
        pileupFileName = sys.argv[1]
        opFileName = sys.argv[2]
        step = int(sys.argv[3])
        scaffListFileName = sys.argv[4]
        scaffSets = getScaffsets(scaffListFileName)
        getIntsum(pileupFileName, step, opFileName, set(['CGS00001', 'CGS32590']))
    else:
        print err
  
                
            
if __name__=='__main__':
    main()
