import sys
import os

""" takes input scaffold file, outputs all FASTA sequences in corresponding
seaprate file named after header into output directory"""
def splitFasta(scaffsFileName, outDir):
    with open(scaffsFileName, 'r') as scaffsFile:
        tempOutFile = None
        try:
            for line in scaffsFile:
                if line.startswith('>'):
                    #found header
                    newFileName = (line.rstrip('\n'))[1:]+'.fasta'
                    tempOutFile = open(os.path.join(outDir, newFileName), 'w')
                    tempOutFile.write(line)
                else:
                    #found sequence
                    tempOutFile.write(line)
                    tempOutFile.close()
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)


def main():
    argLen = len(sys.argv)
    if argLen >= 3:
        scaffsFileName = sys.argv[1]
        outDir = sys.argv[2]
        splitFasta(scaffsFileName, outDir)
    else:
        print 'err: less num of args passed'
    


if __name__ == '__main__':
    main()
