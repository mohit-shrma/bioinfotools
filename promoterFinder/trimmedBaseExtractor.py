""" this script will extract the 100 base pair from the trimmed region and
upto 1900 base pairs behind it """
import sys

""" contains the column number from the promoter trimmed file information  """
class PromoterTrimConsts:
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

    #promoter trim length col
    PROM_TRIM_LEN_COL = 7

""" from the trimmed promoter file name read the data and
output trimmed promoter region with 100bp from trimmed region and
1900 bp from region behind it """
def getTrimmedPromoters(promoterFileName, allScaffoldFileName,\
                            trimPromoterOutName):
    with open(promoterFileName, 'r') as promoterStatsFile:
        with open(trimPromoterOutName, 'w') as trimPromoterOutFile:
            with  open(trimPromoterOutName+'_tab', 'w') as trimPromoterTabFile:
                #read header if there
                #header = promoterStatsFile.readline()
                currScaffName = ''
                currScaffLen = -1
                currScaffBases = ''
                for line in promoterStatsFile:
                    cols = line.rstrip('\n').split('\t')
                    #get promoter header
                    #TODO: check col No. header for promoter in promoter bases file
                    promoterHeader = cols[PromoterTrimConsts.PROM_HEADER]
                    #get promoter details
                    promoterSymbol = cols[PromoterTrimConsts.FEATURE_SYMBOL_COL]
                    #get promoter direction
                    promoterDirection = cols[PromoterTrimConsts.PROM_DIR_COL]
                    #get promoter start
                    promoterStart = int(cols[PromoterTrimConsts.SCAFF_START_COL])-1
                    #get promoter end
                    promoterEnd = int(cols[PromoterTrimConsts.SCAFF_END_COL])-1
                    #get scaff name
                    promoterScaffName = cols[PromoterTrimConsts.SCAFF_NAME_COL]
                    #get promoter trim length
                    promoterTrimLength = cols[PromoterTrimConsts.PROM_TRIM_LEN_COL]
                    #get promoter details
                    promoterDetails = cols[PromoterTrimConsts.FEATURE_DETAILS_COL]

                    if promoterSymbol == "N.A.":
                        continue

                    if currScaffName != promoterScaffName:
                        #current scaffold bases  is not
                        #equal to require scaffold by predictor
                        currScaffBases = getScaffBases(promoterScaffName, \
                                                           allScaffoldFileName)
                        if len(currScaffBases) <= 0:
                            #desired scaffold not found
                            continue
                        currScaffName = promoterScaffName
                        #flush the output files

                    if promoterTrimLength <=0:
                        #TODO?
                        continue

                    if promoterDirection == '+':
                        # 'atg'
                        #get the promotertrimmed position behind promoter End
                        #or after promoter start
                        # -1 to convert it to zero index 
                        promoterTrimPos = promoterEnd - promoterTrimLength - 1
                        #get the 1900 bases before 'promoterTrimPos'
                        trimStart = promoterTrimPos - 1900
                        #get the 100 bases after trim pos including trim pos
                        trimEnd = promoterTrimPos + 99
                        if trimStart < 0:
                            #going behind the scaffold start
                            trimStart = 0
                        if trimEnd >= promoterEnd - 1:
                            #going beyond the promoter end
                            trimEnd = promoterEnd - 1
                    elif promoterDirection == '-':
                        # 'cat'
                        #get the promotertrimmed position behind promoter End
                        #or after promoter start
                        # -1 to convert it to zero index
                        promoterTrimPos = promoterStart + promoterTrimLength - 1
                        #get the 100 bases before trim pos including trim pos
                        trimStart = promoterTrimPos - 99
                        #get the 1900 bases after 'promoterTrimPos' 
                        trimEnd = promoterTrimPos + 1900
                        if trimStart < promoterStart - 1:
                            #going behind promoter start region
                            trimStart = promoterStart - 1
                        if trimEnd > currScaffLen - 1:
                            #going beyond the scaffold length
                            trimEnd = currScaffLen - 1

                    #get the trimmed bases from with in current scaffold
                    trimmedBases = currScaffBases[trimStart:trimEnd + 1]

                    #header
                    trimHeader = '>'+promoterHeader

                    #write it out to promoter trim output file
                    trimPromoterOutFile.write(trimHeader + '\n')

                    #write the promoter bases
                    trimPromoterOutFile.write(trimmedBases + '\n')

                    #write out trimmed promoter information
                    trimPromoterTabFile.write(promoterScaffName + '\t'\
                                                  + promoterHeader + '\t'\
                                                  + promoterSymbol + '\t'\
                                                  + promoterStart + '\t'\
                                                  + promoterEnd + '\t'\
                                                  + promoterDirection + '\t'\
                                                  + promoterTrimLength + '\t'\
                                                  + trimStart + '\t'\
                                                  + trimEnd + '\n')
                
                    
                    
                        
                        
                    

    
                

    
                
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
        #read the trimmed promoter file name
        promoterFileName = sys.argv[1]
        #get file name containing all the scaffolds
        allScaffoldFileName = sys.argv[2]
        #get file name for new trimmed promoter output bases
        trimPromoterOutName = sys.argv[3]
        getTrimmedPromoters(promoterFileName, allScaffoldFileName,\
                                trimPromoterOutName)
        
    else:
        print 'err: files missing'
    

if __name__ == '__main__':
    main()



