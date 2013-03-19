import sys
import os


def getSixthSNP(ipDir, prefix):
    fifthSNP = os.path.join(ipDir, prefix + '_5' + '.' + FileExts.SNP)
    sixthSNP = os.path.join(ipDir, prefix + '_6' + '.' + FileExts.SNP)
    with open(fifthSNP, 'r') as fifthSNPFile:
        with open(sixthSNP, 'w') as sixthSNPFile:
            for line in fifthSNPFile:
                line = line.strip()
                cols = line.split('\t')
                if len(cols) > 28:
                    print 'exceeded columns limit'
                newCols = cols[23:28] + cols[0:23]
                sixthSNPFile.write('\t'.join(newCols) + '\n')


def main():
    if len(sys.argv) >= 3:
        ipDir = sys.argv[1]
        prefix = sys.argv[2]
        getSixthSNP(ipDir, prefix)
    else:
        print 'err: '
                
if __name__=='__main__':
    main()
