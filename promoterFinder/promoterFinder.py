import sys

class PredictionFileConsts:
    #scaffold name col
    SCAFF_NAME_COL=0

    #start col
    SCAFF_START_COL = 3

    #end col
    SCAFF_END_COL = 4

    #feature column
    FEATURE_COL = 6

    #promoter length
    PROM_LENGTH = 3000

    
""" output promter to separate file by reading 3000 bases before the\
start sites in gene prediction
NOTE: this assumes that the file passed to this is sorted by scaffold name for 
efficient computation
"""
def getPromotersFromPredicter(predictionFileName, allScaffoldFileName,\
                                  promoterOutputFileName):
    promoterCount = 0
    with open(predictionFileName, 'r') as predictionFile:
        with open(promoterOutputFileName, 'w') as promoterOutFile:
            with open(promoterOutputFileName+'.tab', 'w') as promoterTabFile:
                
                currScaffName = ''
                currScaffBases = ''
                for line in predictionFile:
                    #get the required data about current feature
                    cols = line.rstrip('\n').split()
                    scaffName = cols[PredictionFileConsts.SCAFF_NAME_COL]
                    #get start and end indices, "-1" as these starts from 1,
                    #and python index starts from 0
                    start = int(cols[PredictionFileConsts.SCAFF_START_COL]) - 1
                    feature = cols[PredictionFileConsts.FEATURE_COL]
                    if currScaffName != scaffName:
                        #current scaffold bases  is not
                        #equal to require scaffold by predictor
                        currScaffBases = getScaffBases(scaffName, \
                                                           allScaffoldFileName)
                        currScaffName = scaffName
                        if len(currScaffBases) == 0:
                            #desired scaffold not found
                            break
                
                    #find the promoter start
                    promoterStart = start - PredictionFileConsts.PROM_LENGTH
                    if promoterStart < 0:
                        if start > 0:
                            promoterStart = 0
                        else:
                            promoterStart = -1
                    
                    #find the promoter end
                    promoterEnd = start - 1
                    if promoterEnd < 0:
                        promoterEnd = promoterStart

                    #promoter bases are [promoterStart to promoterEnd] of
                    #current scaff#including start and end indices
                    promoterBases = currScaffBases[promoterStart:promoterEnd+1]
                    #write header
                    currPromHeader = '>P' + promoterCount + '_' + scaffName\
                                       + '_' + feature
                    promoterOutFile.write(currPromHeader + '\n')
                    #write promoter bases
                    promoterOutFile.write(promoterBases+'\n')

                    #write promoter information along with promoter header
                    #in promoter file
                    promoterTabFile.write(line.rstrip('\n') + '\t' + \
                                              currPromHeader + '\n')
                    promoterCount += 1
                    
                    

"""" get scaffold bases from the scaffolds file """                
def getScaffBases(scaffName, allScaffoldFileName):
    with open(allScaffoldFileName, 'r') as allScaffFile:
        for line in allScaffFile:
            if line.startswith('>'+scaffName):
                #got the desired scaffold
                bases = allScaffFile.readline()
                bases = bases.rstrip('\n')
                return bases
        print 'Error '+ scaffName + ' was not found'
        return ''
        
    

def main():
    if len(sys.argv) >= 3:
        #read the prediction file name
        predictionFileName = sys.argv[1]
        #get file name containing all the scaffolds
        allScaffoldFileName = sys.argv[2]
        #get file name for promoter output
        promoterOutputFileName = sys.argv[3]
        #find promoter corresponding to these predictor
        getPromotersFromPredicter(predictionFileName, allScaffoldFileName,\
                                      promoterOutputFileName)
    else:
        print 'err: files missing'
    

if __name__ == '__main__':
    main()
