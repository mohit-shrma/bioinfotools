import sys
import os
import csv
import numpy as np
import matplotlib
from pylab import *


class Pileup_Consts:
    SCAFF_NAME = 0
    BASE_POS = 1
    COUNT = 3



def plotPileups(pileUpFileName, intervalSize, stepSize):
    with open(pileUpFileName, 'r') as pileUpFile:
        pileUpReader = csv.reader(pileUpFile, delimiter='\t')
        prevScaffName = ''
        prevScaffBase = -1
        #store sum of step size sequences
        stepSums = []
        
        #number of steps per interval
        numStepsPerInt = intervalSize/step

        #sum per step
        sum = 0
        
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

                    #get sum per interval
                    sumsPerInt = []
                    currIntSum = 0
                    
                    for i in range(len(stepSums)):
                        currIntSum += stepSums[i]
                        if (i+1) % numStepsPerInt == 0:
                            #got last step of the interval
                            sumsPerInt.append(currIntSum)
                            currIntSum -= stepSums[i + 1 - numStepsPerInt]
                            
                    #add last interval sum
                    sumsPerInt.append(currIntSum)
                    
                    #plot sumsPerInt for previous scaffold
                    createPlot(prevScaffName, sumsPerInt, prevScaffBase)
                    
                #initialize parameters for new scaffold
                basePos = int(row[Pileup_Consts.BASE_POS])
                prevScaffBase = basePos
                count = int(row[Pileup_Consts.COUNT])
                sum = count

                

#create plot with 'name' and y values in seq
def createPlot(name, seq, size, plotDir=None):

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
    plot(seq)
    
    #save figure
    savefig(os.path.join(plotDir, name + '.png'))    
    
                
    

def main():
    if len(sys.argv) > 3:
        pileUpFileName = os.path.abspath(sys.argv[1])
        intervalSize = int(sys.argv[2])
        stepSize = int(sys.argv[3])
        
    else:
        print 'err: invalid args'
        

if __name__ == '__main__':
    main()
