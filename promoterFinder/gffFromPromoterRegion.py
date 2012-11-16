""" create gff file for promoter regions  """

import sys
import os

class PromoterConsts:

    #scaffold name col
    SCAFF_COL = 2

    #promoter header col
    PROM_HEADER_COL = 0

    #promoter start
    PROM_START = 3

    #promoter end
    PROM_END = 4

    #promoter direction
    PROM_DIR = 5

    #promoter symbol
    PROM_SYM = 7

    #promoter trim start
    PROM_TRIM_START = 8

    #promoter trim end
    PROM_TRIM_END = 9

    #promoter details
    PROM_DETAIL = 10

def generateGFFForScaffolds(trimPromFileName, gffDirName):
    with open(trimPromFileName, 'r') as trimPromFile:

        #store current scaffold name
        currScaffName = ''
        currScaffFile = ''
        for line in trimPromFile:
            cols = line.rstrip('\n').split('\t')

            promoterHeader = cols[PromoterConsts.PROM_HEADER_COL]
            promoterTrimStart = cols[PromoterConsts.PROM_TRIM_START]
            promoterTrimEnd = cols[PromoterConsts.PROM_TRIM_END]
            promoterDirection = cols[PromoterConsts.PROM_DIR]
            promoterSymbol = cols[PromoterConsts.PROM_SYM]
            promoterDetails = cols[PromoterConsts.PROM_DETAIL]
            promoterScaffold = cols[PromoterConsts.SCAFF_COL]

            if currScaffName != promoterScaffold:
                #current scaffold being worked on is different from new one
                try:
                    if currScaffFile != '':
                        #close the last opened file
                        currScaffFile.close()
                    currScaffFile = open(os.path.join(gffDirName,\
                                                          promoterScaffold\
                                                          + '.gff3'), 'w')
                    currScaffFile.write('NAME\tSOURCE\tTYPE\tSTART\tEND'\
                                            + '\tSCORE\tSTRAND\tFRAME\tGROUP')
                    currScaffName = promoterScaffold
                except IOError as e:
                     print "I/O error({0}): {1}".format(e.errno, e.strerror)

            #write details in gff file
            #NAME  SOURCE  TYPE  START  END  SCORE  STRAND  FRAME  GROUP
            currScaffFile.write(promoterScaffold + '\t' + '.' + '\t'\
                                    + promoterSymbol + '\t' + promoterTrimStart\
                                    + '\t' + promoterTrimEnd + '\t' + '.' \
                                    + '\t' + promoterDirection + '\t' + '.'\
                                    + '\t' + 'Name=' + promoterSymbol\
                                    + ';Note=' + promoterDetails\
                                    + ';ID=' + promoterHeader +'\n')
        if currScaffFile != '':
            #close the last opened file
            currScaffFile.close()
    

            
class GFFConsts:
    
    #gff output file extension
    GFF_EXT = '.gff'
    
            
def main():
    argLen =  len(sys.argv)
    if argLen >= 3:
        trimPromFileName = sys.argv[1]
        gffDirName = sys.argv[2]
        #check if passed dirname is dir or not
        if os.path.isdir(gffDirName):
            #for each scaff in trimmed promoter file 
            generateGFFForScaffolds(trimPromFileName, gffDirName)

    else:
        print 'err: files missing'



if __name__ == '__main__':
    main()

    
