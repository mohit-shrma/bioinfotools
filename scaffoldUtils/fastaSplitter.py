import sys
import os


""" takes input scaffold file, outputs all FASTA sequences in corresponding
seaprate file named after header into output directory,
optional cutOffLen can be provided for sequences to be ignored"""
def splitFasta(scaffsFileName, outDir, cutOffLen = None):
    with open(scaffsFileName, 'r') as scaffsFile:
        header = None
        for line in scaffsFile:
            if line.startswith('>'):
                #found header
                header = line.rstrip('\n')
            else:
                #found sequence
                if cutOffLen is not None:
                    if (len(line) - 1) >= cutOffLen: # -1 for '\n'
                        #sequence length is gr8r than cutoff len
                        #write out corresponding sequence & header
                        writeOutSeq(header, line.rstrip('\n'), outDir)
                else:
                    #write out corresponding sequence & header
                    writeOutSeq(header, line.rstrip('\n'), outDir)

                    

""" write the header and sequence into a file in outDir, e.g. if header='>SN1',
then it creates a file with name SN1.fasta and write out the sequence """
def writeOutSeq(header, sequence, outDir):
    fileName = header[1:] + '.fasta'
    with open(os.path.join(outDir, fileName), 'w') as tempOutFile:
        #write header
        tempOutFile.write(header + '\n')
        #write sequence
        tempOutFile.write(sequence + '\n')
            

def main():
    argLen = len(sys.argv)
    if argLen >= 4:
        scaffsFileName = sys.argv[1]
        outDir = sys.argv[2]
        cutOffLen = int(sys.argv[3])
        splitFasta(scaffsFileName, outDir, cutOffLen)
    elif argLen >= 3:
        scaffsFileName = sys.argv[1]
        outDir = sys.argv[2]
        splitFasta(scaffsFileName, outDir)
    else:
        print 'err: less num of args passed'
    


if __name__ == '__main__':
    main()
