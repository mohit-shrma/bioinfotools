import sys
import os
import csv

from plotPileupCoverage import *


class CompPileup:
    
    def __init__(self, pileup1Dir, pileup2Dir, loThresh, hiThresh, \
                     intervalSize, stepSize, \
                     plot1Dir, plot2Dir, plotCmpDir):
        self.pileup1Dir = pileup1Dir
        self.pileup2Dir = pileup2Dir
        self.loThresh = loThresh
        self.hiThresh = hiThresh
        self.intervalSize = intervalSize
        self.stepSize = stepSize
        self.plot1Dir = plot1Dir
        self.plot2Dir = plot2Dir
        self.plotCmpDir = plotCmpDir
        


    def getParamDic(self):
        myDic = {}
        myDic['pileup1Dir'] = self.pileup1Dir
        myDic['pileup2Dir'] = self.pileup2Dir
        myDic['loThresh'] = self.loThresh
        myDic['hiThresh'] = self.hiThresh
        myDic['intervalSize'] = self.intervalSize
        myDic['stepSize'] = self.stepSize
        myDic['plot1Dir'] = self.plot1Dir
        myDic['plot2Dir'] = self.plot2Dir
        myDic['plotCmpDir'] = self.plotCmpDir
        return myDic


#compare two pileups with the passed scaffold name
def compareTwoPileups((dic, scaffName)):
    #get pileup file name in dir1
    pileup1Path = os.path.join(dic['pileup1Dir'], scaffName + '.'\
                                   + Pileup_Consts.PILEUP_EXT)
    pileup2Path = os.path.join(dic['pileup2Dir'], scaffName + '.'\
                                   + Pileup_Consts.PILEUP_EXT)
    #check for the existence of file
    if (not os.path.isfile(pileup1Path)) or\
            (not os.path.isfile(pileup2Path)):
        #either of file not found then exit
        return -1

    #get the corresponding stepsums
    stepSum1 = getStepSums(pileup1Path, dic['intervalSize'], dic['stepSize'])
    stepSum2 = getStepSums(pileup2Path, dic['intervalSize'], dic['stepSize'])

    #exit if failed to get either
    if len(stepSum1) == 0 or len(stepSum2) == 0:
        return -1

    #number of steps per interval
    numStepsPerInt = dic['intervalSize']/dic['stepSize']

    #get the moving average of step intervals
    (sumsPerInt1, threshExceedingCount1)  = getMovingAvg(stepSum1,\
                                                             numStepsPerInt,\
                                                             dic['intervalSize'],\
                                                             dic['loThresh'],\
                                                             dic['hiThresh'])

    (sumsPerInt2, threshExceedingCount2)  = getMovingAvg(stepSum2,\
                                                             numStepsPerInt,\
                                                             dic['intervalSize'],\
                                                             dic['loThresh'],
                                                             dic['hiThresh'])

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

    if threshExceedingCount1 > 10 or threshExceedingCount2 > 10 \
           or maxR > 2 or minR < 0.5:
    #if True:
        #create corresponding scatter plots
        #createPlot(scaffName, sumsPerInt1, numStepsPerInt, dic['plot1Dir'])
        #createPlot(scaffName, sumsPerInt2, numStepsPerInt, dic['plot2Dir'])
        createPlot(scaffName, ratio, numStepsPerInt, dic['plotCmpDir'], 4, -4)

    return 1


def compSerialWorkers(dic, scaffListName):

    workerArgs = []

    #parse the file to get the scaffs
    with open(scaffListName, 'r') as scaffListFile:
        for line in scaffListFile:
            line = line.strip()
            workerArgs.append(line)

    for scaffName in workerArgs:
        res = compareTwoPileups((dic,scaffName))
        print 'compared: ', scaffName, ' ', res



def compWorkers(dic, scaffListName, cpuCount):

    workerArgs = []

    #parse the file to get the scaffs
    with open(scaffListName, 'r') as scaffListFile:
        for line in scaffListFile:
            line = line.strip()
            workerArgs.append((dic,line))

    #initialize pool with number of possible jobs
    pool = Pool(processes=min(len(workerArgs), cpuCount))

    results = pool.map(compareTwoPileups, workerArgs)

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
        loThresh = int(sys.argv[6])
        hiThresh = int(sys.argv[7])
        plot1Dir = sys.argv[8]
        plot2Dir = sys.argv[9]
        plotCmpDir = sys.argv[10]
        cpuCount = sys.argv[11]
        
        cmpPileup  = CompPileup(pileup1Dir, pileup2Dir, loThresh, hiThresh, \
                     intervalSize, stepSize, \
                     plot1Dir, plot2Dir, plotCmpDir)
        dic = cmpPileup.getParamDic()
        compWorkers(dic, scaffListName, cpuCount)
        #compSerialWorkers(dic, scaffListName)
    else:
        print 'err: invalid args'


if __name__ == '__main__':
    main()
