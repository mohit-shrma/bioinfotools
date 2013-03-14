import sys
import os
import csv

from plotPileupCoverage import *


class CompPileup:
    
    def __init__(self, pileup1Dir, pileup2Dir, thresh1, thresh2, \
                     intervalSize, stepSize, \
                     plot1Dir, plot2Dir, plotCmpDir):
        self.pileup1Dir = pileup1Dir
        self.pileup2Dir = pileup2Dir
        self.thresh1 = thresh1
        self.thresh2 = thresh2
        self.intervalSize = intervalSize
        self.stepSize = stepSize
        self.plot1Dir = plot1Dir
        self.plot2Dir = plot2Dir
        self.plotCmpDir = plotCmpDir
        

    #compare two pileups with the passed scaffold name
    def compareTwoPileups(self, scaffName):
        #get pileup file name in dir1
        pileup1Path = os.path.join(self.pileup1Dir, scaffName + '.'\
                                       + Pileup_Consts.PILEUP_CONSTS)
        pileup2Path = os.path.join(self.pileup2Dir, scaffName + '.'\
                                       + Pileup_Consts.PILEUP_CONSTS)
        #check for the existence of file
        if (not os.path.isfile(pileup1Path)) or\
                (not os.path.isfile(pileup2Path)):
            #either of file not found then exit
            return -1

        #get the corresponding stepsums
        stepSum1 = getStepSums(pileup1Path, self.intervalSize, self.stepSize)
        stepSum2 = getStepSums(pileup2Path, self.intervalSize, self.stepSize)

        #exit if failed to get either
        if len(stepSum1) == 0 or len(stepSum2) == 0:
            return -1
        
        #number of steps per interval
        numStepsPerInt = self.intervalSize/self.stepSize
        
        #get the moving average of step intervals
        (sumsPerInt1, threshExceedingCount1)  = getMovingAvg(stepSum1,\
                                                                numStepsPerInt,\
                                                                self.intervalSize,\
                                                                 self.thresh1)
        
        (sumsPerInt2, threshExceedingCount2)  = getMovingAvg(stepSum2,\
                                                                numStepsPerInt,\
                                                                self.intervalSize,\
                                                                 self.thresh2)
        
        if len(sumsPerInt1) != len(sumsPerInt2):
            print 'difference in values of sums per interval: ', scaffName

        #get ratio of sumsPerInt across two pilleup
        ratio = array('d', [])
        maxR = -1
        minR = 500
        for i in range(min(len(sumsPerInt1), len(sumsPerInt2))):
            if sumsPerInt2[i] > 0:
                r = float(sumsPerInt1[i])/float(sumsPerInt2[i])
            else:
                r = float(sumsPerInt1[i])
            if r > maxR:
                maxR = r
            if r < minR:
                minR = r
            ratio.append(r)

        print 'scaffold: ', scaffName, ' len(sumsPerInt1): ', len(sumsPerInt1),\
            'threshExceedingCount1: ', threshExceedingCount1,\
            ' len(sumsPerInt1): ', len(sumsPerInt1),\
            ' threshExceedingCount2: ', threshExceedingCount2, \
            ' len(ratio): ', len(ratio)
        
        if threshExceedingCount1 > 0 or threshExceedingCount2 > 0 \
                or maxR > 2 or minR < 0.5:
            #create corresponding scatter plots
            createPlot(scaffName, sumsPerInt1, numStepsPerInt, self.plot1Dir)
            createPlot(scaffName, sumsPerInt2, numStepsPerInt, self.plot2Dir)
            createPlot(scaffName, ratio, numStepsPerInt, self.plotCmpDir)



def compWorkers(scaffListName, cmpPileUp, cpuCount):
    
    workerArgs = []

    #parse the file to get the scaffs
    with open(scaffListName, 'r') as scaffListFile:
        for line in scaffListFile:
            line = line.strip()
            workerArgs.append(line)

    #initialize pool with number of possible jobs
    pool = Pool(processes=min(len(workerArgs), cpuCount))

    results = pool.map(cmpPileUp.compareTwoPileups, workerArgs)
    
    pool.close()
    pool.join()

    return results


def main():
    if len(sys.argv) > 4:
        scaffListName = sys.argv[1]
        pileup1Dir = sys.argv[2]
        pileup2Dir = sys.argv[3]
        intervalSize = int(sys.argv[4])
        stepSize = int(sys.argv[5])
        thresh1 = int(sys.argv[6])
        thresh2 = int(sys.argv[7])
        plot1Dir = sys.argv[8]
        plot2Dir = sys.argv[9]
        plotCmpDir = sys.argv[10]
        cpuCount = sys.argv[11]
        
        cmpPileup  = CompPileup(pileup1Dir, pileup2Dir, thresh1, thresh2, \
                     intervalSize, stepSize, \
                     plot1Dir, plot2Dir, plotCmpDir)
        compWorkers(scaffListName, cmpPileup, cpuCount)
    else:
        print 'err: invalid args'



if __name__ == '__main__':
    main()
