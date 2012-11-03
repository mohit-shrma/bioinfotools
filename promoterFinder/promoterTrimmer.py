""" based on the EST sequences, trim the promoter,
using bisect module for maintaining sorted list"""
import sys
from bisect import *


""" contains col number for promoter file"""
class PromoterFileConsts:
    #scaffold name col
    SCAFF_NAME_COL = 2

    #start col
    SCAFF_START_COL = 3

    #end col
    SCAFF_END_COL = 4

    #feature type column
    FEATURE_TYPE_COL = 1

    #note carefully to split on tab separated as normal spaces can be
    #inserted sometime in files
    #feature symbol column
    FEATURE_SYMBOL_COL = 6
    
    #feature detals column
    FEATURE_DETAILS_COL = 7

    #promoter direction
    PROM_DIR_COL = 5

    #promoter header
    PROM_HEADER = 0
    
""" contains col number for EST file"""
class ESTFileConsts:
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


#return the sorted gene symbols
def sortedPredGeneSymbols(promoterFileName):
    geneSymbols = []
    with open(promoterFileName, 'r') as promoterFile:
        for line in promoterFile:
            cols = line.rstrip('\n').split('\t')
            featureSymbol = cols[PromoterFileConsts.FEATURE_SYMBOL_COL]
            #Locate the leftmost value exactly equal to featureSymbol
            i = bisect_left(geneSymbols, featureSymbol)
            if i == len(geneSymbols) or geneSymbols[i] != featureSymbol:
                #not found in sorted list, insert in sorted list
                geneSymbols.insert(i, featureSymbol)
    return geneSymbols
            

#return the symbols dictionary in following form
# {symbol:[scaffName1:[(minStart, end), (start, maxEnd)],
#          scaffName2:[(minStart, end), (start, maxEnd)]],
#  symbol2:[...]}        
def getESTSymbolsDict(predSymbols, estFileName):
    symbolsDict = {}
    with open(estFileName, 'r') as estFile:
        for line in estFile:
            cols =line.rstrip('\n').split('\t')
            
            #get est symbol
            estSymbol = cols[ESTFileConsts.FEATURE_SYMBOL_COL]
            #get symbol details
            scaffName = cols[ESTFileConsts.SCAFF_NAME_COL]
            #get start and end, sub -1 as python works in 0-index based
            #and value in file 1-index based
            start = int(cols[ESTFileConsts.SCAFF_START_COL]) - 1
            end = int(cols[ESTFileConsts.SCAFF_END_COL]) - 1

            #TODO: think about lower case comparison
            if estSymbol not in symbolsDict:
                #search for estsymbols in sorted pred symbols
                i = bisect_left(predSymbols, estSymbol)
                if i != len(predSymbols) \
                        and predSymbols[i] == estSymbol:
                    #value present in pred symbol list
                    #enter symbol details in dict
                    symbolsDict[estSymbol] = {scaffName:[(start, end),\
                                                        (start, end)]}
                else:
                    #symbol not in pred symbol, don't do anything
                    pass
            else:
                #est symbol present in dict
                estSymbolDict = symbolsDict[estSymbol]
                #search for scaff name in dict value
                if scaffName in estSymbolDict:
                    #found scaffold for this symbol
                    #get minstart and maxstart pair
                    minMaxTuples = estSymbolDict[scaffName]
                    minStart = minMaxTuples[0][0]
                    maxEnd = minMaxTuples[1][1]
                    #update minStart
                    if minStart > start:
                        minMaxTuples[0] = (start, end)
                    #update maxEnd
                    if maxEnd < end:
                        minMaxTuples[1] = (start, end)
                    #update symbold dict with new min max values
                    estSymbolDict[scaffName] = minMaxTuples
                else:
                    #scaffold not found in symbol
                    #enter scaffold details in symbol dict, as minMax tuples
                    estSymbolDict[scaffName] = [(start, end), (start, end)]
                #update symbols dict
                symbolsDict[estSymbol] = estSymbolDict
        #closes for, return symbols dictionary
        return symbolsDict

#based on est symbols trim promoters and output trimmed length in file
def writeTrimPromoters(estSymbolsDict, promoterFileName, trimPromoterFileName):
    with open(promoterFileName, 'r') as promoterFile:
        with open(trimPromoterFileName, 'w') as trimPromoterFile:
            for line in promoterFile:
                cols = line.rstrip('\n').split('\t')
                #get promoter header
                promoterHeader = cols[PromoterFileConsts.PROM_HEADER]
                #get promoter details
                promoterSymbol = cols[PromoterFileConsts.FEATURE_SYMBOL_COL]
                #get promoter direction
                promoterDirection = cols[PromoterFileConsts.PROM_DIR_COL]
                #get promoter start
                promoterStart = int(cols[PromoterFileConsts.SCAFF_START_COL])-1
                #get promoter end
                promoterEnd = int(cols[PromoterFileConsts.SCAFF_END_COL])-1
                #get scaff name
                promoterScaffName = cols[PromoterFileConsts.SCAFF_NAME_COL]
                #get promoter details
                promoterDetails = cols[PromoterFileConsts.FEATURE_DETAILS_COL]
                #initialize trimlength
                trimLength = 0
                if promoterSymbol in estSymbolsDict:
                    #get EST symbol details for this symbol
                    estSymbolDict = estSymbolsDict[promoterSymbol]
                    if promoterScaffName in estSymbolDict:
                        #get minMaxTuples for current scaff
                        minMaxTuples = estSymbolDict[promoterScaffName]
                        trimLength = -786
                        if promoterDirection == '+':
                            #'ATG' case promoter before the sequence,
                            #take the min start
                            minStart = minMaxTuples[0][0]
                            end = minMaxTuples[0][1]
                            if promoterStart <= minStart\
                                    and promoterEnd >= minStart:
                                #trim promoter, if minStart lies in between
                                #promoterStart and promoter end
                                #i.e. EST overlaps
                                trimLength = promoterEnd - minStart + 1
                            elif minStart > promoterEnd:
                                #dont trim promoter,
                                #EST region to right of promoter
                                print promoterScaffName, ' EST: ', str(minStart+1), str(end+1),\
                                    ' to right of \'+\' promoter: ', \
                                    promoterSymbol, str(promoterStart+1), str(promoterEnd+1)
                                trimLength = 'N.A.'
                            else:
                                #weird case, EST lies to left of promoter in '+' dir
                                print promoterScaffName, 'EST: ', str(minStart+1), str(end+1),\
                                    ' to left of \'+\' promoter: ', \
                                    promoterSymbol, str(promoterStart+1), str(promoterEnd+1)
                                trimLength = 'N.A.'

                            #if minStart == -1:
                            #    trimLength = 'N.F.'

                        else:
                            #'CAT' case promoter after the sequence,
                            #take the max end
                            maxEnd = minMaxTuples[1][1]
                            start = minMaxTuples[1][0]
                            if maxEnd <= promoterEnd\
                                    and maxEnd >= promoterStart:
                                #trim promoter, maxEnd lies in between promoter
                                #i.e. EST overlaps
                                trimLength = maxEnd - promoterStart + 1
                            elif maxEnd < promoterStart:
                                #dont trim promoter,EST lies to left of promoter
                                print promoterScaffName, 'EST: ', str(start+1), str(maxEnd+1),\
                                    ' to left of \'-\' promoter: ', \
                                    promoterSymbol, str(promoterStart+1), str(promoterEnd+1)
                                trimLength = 'N.A.'
                            else:
                                #weird case,EST lies to right of promoter in '-' dir
                                print promoterScaffName, 'EST: ', str(start+1), str(maxEnd+1),\
                                    ' to right of \'-\' promoter: ', \
                                    promoterSymbol, (promoterStart+1), str(promoterEnd+1)
                                trimLength = 'N.A.'
                            
                #write to trimmed promoter file
                trimPromoterFile.write(promoterHeader + '\t'\
                                           + "PromoterPrediction" + '\t'\
                                           + promoterScaffName + '\t'\
                                           + str(promoterStart+1) + '\t'\
                                           + str(promoterEnd+1) + '\t'\
                                           + promoterDirection +'\t'\
                                           + str(trimLength) + '\t'\
                                           + promoterSymbol + '\t'\
                                           + promoterDetails + '\n')
    

def main():
    if len(sys.argv) >= 3:
        #read the promoter file name
        promoterFileName = sys.argv[1]
        #get file name for EST
        estFileName = sys.argv[2]
        #get file name for trimmed promoter output
        trimPromoterFileName = sys.argv[3]
        #get the valid gene symbols in sorted list
        predSymbols = sortedPredGeneSymbols(promoterFileName)
        #get the EST symbols dcictionary for these symbols
        estSymbolsDict = getESTSymbolsDict(predSymbols, estFileName)
        #based on est symbols trim promoters and output trimmed length in file
        writeTrimPromoters(estSymbolsDict, promoterFileName,\
                               trimPromoterFileName)        
    else:
        print 'err: files missing'
    

if __name__ == '__main__':
    main()

