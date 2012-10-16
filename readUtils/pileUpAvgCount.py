import sys
import os
from pylab import *
import numpy as np
import matplotlib

class SAMConsts:

    #position col
    POSITION_COL = 2
    
    #number of reads col
    NUM_READS_COL = 3

    #reads alignment pos style col
    ALIGN_POS_STYLE_COL = 4

    #reads start style
    START_STYLE = '^F'
    START_STYLE_FIRST = '^'
    START_STYLE_SECOND = 'F'

    #reads end style
    END_STYLE = '$'


def plotAverage(movingAverages, plotFileName):
    #initialize py plot for non interactive backend
    matplotlib.use('Agg')

    #indicate to pyplot that we have new figure
    figure()

    #plot the learned averages
    plot(range(len(movingAverages)), movingAverages, color='b')

    #set the limit on y axis
    ymin, ymax = ylim()   # return the current ylim
    ylim(-1, ymax)
    
    savefig((plotFileName + '.png'))


def writeAverageToFile(movingAverages, opAvgFileName):
    with open(opAvgFileName, 'w') as opAvgFile:
        for avg in movingAverages:
            opAvgFile.write(str(avg) + '\n')

            

def readAverageFromFile(ipAverageFileName):
    movingAverages = [] 
    with open(ipAverageFileName, 'r') as ipAvgFile:
        for avg in ipAvgFile:
            movingAverages.append(int(avg))
    return movingAverages


    
#get the pileups moving average over specified window and a step size
def getAverageWindowPileup(pileupFileName, windowSize, stepSize):
    intervalsAvg = []
    with open(pileupFileName, 'r') as pileupFile:
        numReadsInterval = []
        for line in pileupFile:
            cols = line.split()
            numReads = cols[SAMConsts.NUM_READS_COL]
            numReadsInterval.append(int(numReads))
            
            if len(numReadsInterval) >= windowSize:
                #size of window equals or exceeds specified window size
                avg = sum(numReadsInterval)/windowSize
                intervalsAvg.append(avg)
                #trim down interval by step size
                numReadsInterval = numReadsInterval[stepSize:]
                
        #size of window equals or exceeds specified window size
        avg = sum(numReadsInterval)/windowSize
        intervalsAvg.append(avg)

    return intervalsAvg


def main():
    argLen = len(sys.argv)
    if argLen >= 4:
        #passed pile up file
        pileupFileName = sys.argv[1]
        #window size for moving average
        windowSize = int(sys.argv[2])
        #step size for moving average
        stepSize = int(sys.argv[3])
        #plot output for moving average
        plotFileName = sys.argv[4]
        #compute moving averages
        movingAverages = getAverageWindowPileup(pileupFileName, windowSize, stepSize)
        print movingAverages
        #plot the moving averages
        #plotAverage(movingAverages, plotFileName)
        #write the averages to a file
        writeAverageToFile(movingAverages, plotFileName)
        #read averages from file
        movingAverages = readAverageFromFile(plotFileName)
        print movingAverages
    else:
        print 'err: less num of args passed'

if __name__ == '__main__':
    main()
