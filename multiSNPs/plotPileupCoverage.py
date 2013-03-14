import sys
import os
import csv
import matplotlib
from pylab import *
from multiprocessing import Pool
import multiprocessing, logging
from array import array

class Pileup_Consts:
    SCAFF_NAME = 0
    BASE_POS = 1
    COUNT = 3
    PILEUP_EXT= "mpileup"



def getAllPileups(pileupDir):
    pileUps = []
    dirContents = os.listdir(pileupDir)
    dirContents.sort()
    for file in dirContents:
        if file.endswith(Pileup_Consts.PILEUP_EXT):
            pileUps.append(os.path.join(pileupDir, file))
    return pileUps



#will take input as scaffold pile up file return and return step sum
def getStepSums(pileUpFileName, intervalSize, stepSize):

    #store sum of step size sequences
    stepSums = array('L', [])

    with open(pileUpFileName, 'r') as pileUpFile:
        pileUpReader = csv.reader(pileUpFile, delimiter='\t')
        prevScaffName = ''
        prevScaffBase = -1

        #number of steps per interval
        numStepsPerInt = intervalSize/stepSize

        #sum per step
        sum = 0

        try:

            for row in pileUpReader:
                scaffName = row[Pileup_Consts.SCAFF_NAME]

                if prevScaffName == scaffName:

                    basePos = int(row[Pileup_Consts.BASE_POS])
                    prevScaffBase = basePos

                    count = int(row[Pileup_Consts.COUNT])
                    sum += count
                    if (basePos % stepSize) == 0:
                        #accumulated sum of intervalSize counts
                        stepSums.append(sum)
                        sum = 0
                else:
                    if prevScaffName != '':
                        #found a new scaffold, plot for old scaffold
                        #add pending last sum
                        stepSums.append(sum)

                        #get the moving average of step intervals
                        sumsPerInt = getMovingAvg(stepSums, numStepsPerInt, intervalSize)


                    #initialize parameters for new scaffold
                    basePos = int(row[Pileup_Consts.BASE_POS])
                    prevScaffBase = basePos
                    prevScaffName = scaffName
                    count = int(row[Pileup_Consts.COUNT])
                    sum = count

            #plot the last scaffold
            #add pending last sum
            stepSums.append(sum)

        except csv.Error, e:
            print ('scaffold %s, line %d: %s' % (prevScaffName, pileUpReader.line_num, e))

    return stepSums


def plotPileups((pileUpFileName, intervalSize, stepSize, plotDir)):

        print 'plotPileups', (pileUpFileName, intervalSize, stepSize, plotDir)
        
        if plotDir is None:
            plotDir = os.path.abspath("./pileupPlots")

        stepSums = getStepSums(pileUpFileName, intervalSize, stepSize)
        
        if len(stepSums) == 0:
            print 'can\'t plot: ', pileUpFileName
            return -1

        #number of steps per interval
        numStepsPerInt = intervalSize/stepSize

        #get the moving average of step intervals
        (sumsPerInt, threshExceedingCount)  = getMovingAvg(stepSums, numStepsPerInt, intervalSize)
            
        #plot sumsPerInt for previous scaffold
        if threshExceedingCount > 0:
            scaffPileUpName = os.path.basename(pileUpFileName)
            createPlot((scaffPileUpName.split('.'))[0], sumsPerInt, numStepsPerInt, plotDir)
            
        return 1

    

#get the moving average of step interval
def getMovingAvg(stepSums, numStepsPerInt, intervalSize, thresholdFlag=100): 
    
    threshExceedingCount = 0

    #get sum per interval
    sumsPerInt = array('d', [])
    currIntSum = 0

    #to keep step count
    stepCount = 0
    
    for i in range(len(stepSums)):
        currIntSum += stepSums[i]
        stepCount += 1
        if stepCount % numStepsPerInt == 0:
            #got last step of the interval
            sumsPerInt.append(float(currIntSum)/intervalSize)
            #added sum exceeding threshold
            if (sumsPerInt[-1] > thresholdFlag):
               threshExceedingCount += 1
            currIntSum -= stepSums[i + 1 - numStepsPerInt]
            stepCount = 1
            
    #add last interval sum
    sumsPerInt.append(float(currIntSum)/intervalSize)
                    
    return (sumsPerInt, threshExceedingCount)

                

#create plot with 'name' and y values in seq
def createPlot(name, seq, numStepsPerInt, plotDir=None):

    #get the plot directory
    if plotDir is None:
        #not passed any directory to store plot
        #use Current directory to storeplot
        plotDir = os.path.abspath("./pileupPlots")
        if not os.path.exists(plotDir):
            os.makedirs(plotDir)
    else:
        plotDir = os.path.abspath(plotDir)

    print 'plotting... ', name

    #initialize py plot for non interactive backend
    matplotlib.use('Agg')
    
    #indicate to pyplot that we have new figure
    figure()

    #plot the passed base coverage
    x = map( lambda x:x*numStepsPerInt, range(len(seq)) )
    scatter( x, seq, s=5, color='tomato')

    xmin, xmax = xlim()   # return the current xlim
    xlim(0, xmax)
    
    #save figure
    savefig(os.path.join(plotDir, name + '.png'))    



def pileUpPlotters(pileUpsDir, intervalSize, stepSize, plotDir = None, numProcs = 0):
    workersArgs = []
    pileUps = getAllPileups(pileUpsDir)

    for pileUp in pileUps:
        workersArgs.append((pileUp, intervalSize, stepSize, plotDir))

    jobCount = len(workersArgs)

    if numProcs == 0:
        #get number of processors from env
        numProcs = multiprocessing.cpu_count()
        print 'cpuCount: ', numProcs
        
    #initialize pool with number of possible jobs
    pool = Pool(processes=min(numProcs, jobCount))
    
    results = pool.map(plotPileups, workersArgs)
    pool.close()
    pool.join()
    return results
        
    

def main():
    if len(sys.argv) > 3:
        pileUpDir = os.path.abspath(sys.argv[1])
        intervalSize = int(sys.argv[2])
        stepSize = int(sys.argv[3])

        if len(sys.argv) > 4:
            #number of processors provided by user
            numProcs = int(sys.argv[4])
        else:
            numProcs = 0

        if len(sys.argv) > 5:
            #number of processors provided by user
            plotDir = sys.argv[5]
        else:
            plotDir = 0

        pileUpPlotters(pileUpDir, intervalSize, stepSize, plotDir, numProcs)
    else:
        print 'err: invalid args'
        

if __name__ == '__main__':
    main()
