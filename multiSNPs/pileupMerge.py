import sys
import os

def getIndNCov(line):
    cols = line.rstrip().split()
    scaff = (cols[0])
    ind = int(cols[1])
    cov = (cols[2])
    return (scaff, ind, cov)


def mergePileup(fileName1, fileName2, mergeOpFileName):
    with open(fileName1, 'r') as pileupFile1,\
            open(fileName2, 'r') as pileupFile2,\
            open(mergeOpFileName, 'w') as mergeOpFile:
        
        p1 = pileupFile1.readline()
        p2 = pileupFile2.readline()
        
        while len(p1) > 0 and len(p2) > 0:

            (scaff1, ind1, cov1) = getIndNCov(p1)
            (scaff2, ind2, cov2) = getIndNCov(p2)

            if scaff1 == scaff2:
                #both scaff same
                if ind1 == ind2:
                    #both ind are same
                    #print scaff1, ind1, cov1, scaff2, ind2, cov2
                    mergeOpFile.write('\t'.join(map(str, [scaff1, ind1, cov1,\
                                                   scaff2, ind2, cov2])) + '\n')
                elif ind1 < ind2:
                    #first is behind second
                    while ind1 < ind2 and len(p1) > 0:
                        #print scaff1, ind1, cov1, scaff2, ind1, 0.1
                        mergeOpFile.write('\t'.join(map(str, [scaff1, ind1,\
                                              cov1, scaff2, ind1, 0.1])) + '\n')
                        p1 = pileupFile1.readline()
                        if len(p1) == 0:
                            break
                        (scaff1Old, ind1Old, cov1Old) = (scaff1, ind1, cov1)
                        (scaff1, ind1, cov1) = getIndNCov(p1)
                        if scaff1 == scaff2 and ind1 == ind2:
                            #print scaff1, ind1, cov1, scaff2, ind2, cov2
                            mergeOpFile.write('\t'.join(map(str, [scaff1, ind1,\
                                             cov1, scaff2, ind2, cov2])) + '\n')
                            break
                        if scaff1 == scaff2 and not ind1 < ind2:
                            pileupFile1.seek(-1*len(p1), os.SEEK_CUR)
                            (scaff1, ind1, cov1) = (scaff1Old, ind1Old, cov1Old)
                            pileupFile2.seek(-1*len(p2), os.SEEK_CUR)
                            break
                        if scaff1 != scaff2:
                            break
                elif ind1 > ind2:
                    #second is behind first
                    while ind1 > ind2 and len(p2) > 0:
                        #print scaff1, ind2, 0.1, scaff2, ind2, cov2
                        mergeOpFile.write('\t'.join(map(str, [scaff1, ind2,\
                                              0.1, scaff2, ind2, cov2])) + '\n')
                        p2 = pileupFile2.readline()
                        if len(p2) == 0:
                            break
                        (scaff2Old, ind2Old, cov2Old) = (scaff2, ind2, cov2)
                        (scaff2, ind2, cov2) = getIndNCov(p2)
                        if scaff1 == scaff2 and ind1 == ind2:
                            #print scaff1, ind1, cov1, scaff2, ind2, cov2
                            mergeOpFile.write('\t'.join(map(str, [scaff1, ind1,\
                                             cov1, scaff2, ind2, cov2])) + '\n')
                            break
                        if scaff1 == scaff2 and not ind1 > ind2:
                            pileupFile1.seek(-1*len(p1), os.SEEK_CUR)
                            pileupFile2.seek(-1*len(p2), os.SEEK_CUR)
                            (scaff2, ind2, cov2) = (scaff2Old, ind2Old, cov2Old)
                            break
                        if scaff1 != scaff2:
                            break
            
            if scaff1 != scaff2:
                scaff1Num = int(scaff1.lstrip('s'))
                scaff2Num = int(scaff2.lstrip('s'))
                if scaff1Num < scaff2Num:
                    #first is behind second

                    while scaff1Num < scaff2Num:
                        print 'first is behind second', scaff1Num, scaff2Num
                        #print scaff1, ind1, cov1, scaff1, ind1, 0.1
                        mergeOpFile.write('\t'.join(map(str, [scaff1, ind1,\
                                              cov1, scaff1, ind1, 0.1])) + '\n')
                        p1 = pileupFile1.readline()
                        if len(p1) == 0:
                            break
                        (scaff1, ind1, cov1) = getIndNCov(p1)
                        scaff1Num = int(scaff1.lstrip('s'))
                        if scaff1 == scaff2:
                            #print scaff1, ind1, cov1, scaff2, ind2, cov2
                            mergeOpFile.write('\t'.join(map(str, [scaff1, ind1,\
                                             cov1, scaff2, ind2, cov2])) + '\n')
                            break

                if scaff1Num > scaff2Num:
                    #second is behind first

                    while scaff1Num > scaff2Num:
                        print 'second is behind first', scaff1Num, scaff2Num
                        #print scaff2, ind2, 0.1, scaff2, ind2, cov2
                        mergeOpFile.write('\t'.join(map(str, [scaff2, ind2,\
                                              0.1, scaff2, ind2, cov2])) + '\n')
                        p2 = pileupFile2.readline()
                        if len(p2) == 0:
                            break
                        (scaff2, ind2, cov2) = getIndNCov(p2)
                        scaff2Num = int(scaff2.lstrip('s'))
                        if scaff1 == scaff2:
                            #print scaff1, ind1, cov1, scaff2, ind2, cov2
                            mergeOpFile.write('\t'.join(map(str, [scaff1, ind1,\
                                             cov1, scaff2, ind2, cov2])) + '\n')
                            break
            
            if len(p1) == 0 or len(p2) == 0:
                break

            p1 = pileupFile1.readline()
            p2 = pileupFile2.readline()
        
        if len(p1) > 0:
            #pileup 1 still remains
            while len(p1) > 0:
                (scaff1, ind1, cov1) = getIndNCov(p1)
                #print scaff1, ind1, cov1, scaff1, ind1, 0.1
                mergeOpFile.write('\t'.join(map(str, [scaff1, ind1,\
                                              cov1, scaff1, ind1, 0.1])) + '\n')
                p1 = pileupFile1.readline()

        if len(p2) > 0:
            #pileup 2 still remains
            while len(p2) > 0:
                (scaff2, ind2, cov2) = getIndNCov(p2)
                #print scaff2, ind2, 0.1, scaff2, ind2, cov2
                mergeOpFile.write('\t'.join(map(str, [scaff2, ind2, 0.1,\
                                                scaff2, ind2, cov2])) + '\n')
                p2 = pileupFile2.readline()


def main():
    if len(sys.argv) > 3:
        pileup1FileName = sys.argv[1]
        pileup2FileName = sys.argv[2]
        mergeOpFileName = sys.argv[3]
        mergePileup(pileup1FileName, pileup2FileName, mergeOpFileName)
    else:
        print 'err: invalid args'


if __name__ == '__main__':
    main()
