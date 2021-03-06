import sys


""" this class contains the column number"""
class PredictionFileConsts:
    #scaffold name col
    SCAFF_NAME_COL = 0

    #start col
    SCAFF_START_COL = 3

    #end col
    SCAFF_END_COL = 4

    #feature type column
    FEATURE_TYPE_COL = 1

    #feature symbol column
    FEATURE_SYMBOL_COL = 5
    
    #feature detals column
    FEATURE_DETAILS_COL = 6

    #promoter length
    PROM_LENGTH = 3000

    
""" output promter to separate file by reading 3000 bases before the\
start sites in gene prediction
NOTE: this assumes that the file passed to this is sorted by scaffold name for 
efficient computation
"""
def getPromotersFromPredicter(predictionFileName, allScaffoldFileName,\
                                  promoterOutputFileName):
    promoterCount = 1
    with open(predictionFileName, 'r') as predictionFile:
        with open(promoterOutputFileName, 'w') as promoterOutFile:
            with open(promoterOutputFileName+'.tab', 'w') as promoterTabFile:
                skippedPromoterCount = 0
                currScaffName = ''
                currScaffBases = ''
                #read header from prediction file, it will be unused
                header= predictionFile.readline()
                for line in predictionFile:
                    #get the required data about current feature
                    cols = line.rstrip('\n').split('\t')
                    scaffName = cols[PredictionFileConsts.SCAFF_NAME_COL]
                    #get start and end indices, "-1" as these starts from 1,
                    #and python index starts from 0
                    start = int(cols[PredictionFileConsts.SCAFF_START_COL]) - 1
                    end = int(cols[PredictionFileConsts.SCAFF_END_COL]) - 1
                    featureDetails = cols[PredictionFileConsts.FEATURE_DETAILS_COL]
                    featureType = cols[PredictionFileConsts.FEATURE_TYPE_COL]
                    featureSymbol = cols[PredictionFileConsts.FEATURE_SYMBOL_COL]


                    if featureSymbol == "N.A.":
                        continue

                    #only look for predicted feature type
                    #if not featureType.startswith('Predicted'):
                    #    continue

                    if currScaffName != scaffName:
                        #current scaffold bases  is not
                        #equal to require scaffold by predictor
                        currScaffBases = getScaffBases(scaffName, \
                                                           allScaffoldFileName)
                        if len(currScaffBases) == 0:
                            #desired scaffold not found
                            continue
                        currScaffName = scaffName
                        #flush the output files
                        promoterOutFile.flush()
                        promoterTabFile.flush()


                    #find the current bases start and ending 3 bases
                    #start, start+1, start+2
                    startBases = currScaffBases[start:start+3]
                    #end-2, end-1, end
                    endBases = currScaffBases[end-2:end+1]

                    direction  = ''
                    
                    if startBases.lower() == 'atg':
                        #find the promoter start
                        promoterStart = start - PredictionFileConsts.PROM_LENGTH
                        if promoterStart < 0:
                            #got behind start of current of base
                            if start > 0:
                                promoterStart = 0
                            else:
                                promoterStart = -1
                    
                        #find the promoter end
                        promoterEnd = start - 1
                        if promoterEnd < 0:
                            #end got behind start of current base
                            promoterEnd = promoterStart
                        direction = '+'
                        
                    elif endBases.lower() == 'cat':
                        #find the promoter end
                        #TODO: +1 was not necessary, hence removed verify
                        promoterEnd = end + PredictionFileConsts.PROM_LENGTH
                        if promoterEnd > len(currScaffBases) -1:
                            #exceeded the length of current bases
                            if end < len(currScaffBases) -1:
                                #in this case only last base is our promoter
                                promoterEnd = len(currScaffBases) -1
                            else:
                                promoterEnd = -1

                        #find the promoter start
                        promoterStart = end + 1
                        if promoterStart > len(currScaffBases) -1:
                            promoterStart = promoterEnd
                        direction = '-'    
                    else:
                        print 'promoter bases start and end mismatch:', startBases, endBases
                        continue
                    
                    #promoter bases are [promoterStart to promoterEnd] of
                    #current scaff#including start and end indices
                    promoterBases = currScaffBases[promoterStart:promoterEnd+1]

                    if len(promoterBases) == 0:
                        #don't write empty promoter bases
                        skippedPromoterCount += 1 
                        continue
                    
                    #write header
                    currPromHeader = '>P' + str(promoterCount)
                    promoterOutFile.write(currPromHeader + '\n')
                    #write promoter bases
                    promoterOutFile.write(promoterBases+'\n')

                    #write promoter information along with promoter header
                    #in promoter file
                    promoterTabFile.write(currPromHeader + '\t'\
                                              + "PromoterPrediction" + '\t'\
                                              + currScaffName + '\t'
                                              + str(promoterStart+1) + '\t'\
                                              + str(promoterEnd+1) + '\t'\
                                              + direction +'\t'\
                                              + featureSymbol + '\t'\
                                              + featureDetails + '\n')
                    promoterCount += 1
                    
                print 'skipped promoters: ', skippedPromoterCount
                sys.stdout.flush()    
                #flush the output files
                promoterOutFile.flush()
                promoterTabFile.flush()

                
"""" get scaffold bases from the scaffolds file """                
def getScaffBases(scaffName, allScaffoldFileName):
    with open(allScaffoldFileName, 'r') as allScaffFile:
        foundScaff = False
        for line in allScaffFile:
            if line.startswith('>'+scaffName):
                #got the desired scaffold
                foundScaff = True
            elif foundScaff:
                bases = line.rstrip('\n')
                return bases
        print 'Error '+ scaffName + ' was not found'
        sys.stdout.flush()    
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
