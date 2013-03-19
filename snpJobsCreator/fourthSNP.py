import sys
import os
from scipy.stats import poisson


def getFourthSNP(ipDir, prefix):
    thirdSNP = os.path.join(ipDir, prefix + '_3' + '.' + FileExts.SNP)
    fourthSNP = os.path.join(ipDir, prefix + '_4' + '.' + FileExts.SNP)
    with open(thirdSNP, 'r') as thirdSNPFile:
        with open(fourthSNP, 'w') as fourthSNPFile:
            for line in thirdSNPFile:
                line = line.strip()
                cols = line.split('\t')
                dpVal = ''
                
                for eqTup in cols[1].split(';'):
                    if eqTup.startswith('DP='):
                        dpVal = float(eqTup[3:])
                        break
                
                varReads =  float(cols[7])
                poissonCDF = 1-poisson.cdf(varReads - 1, dpVal*0.01)

                cols.insert(0, str(poissonCDF))
                fourthSNPFile.write('\t'.join(cols) + '\n')


def main():
    if len(sys.argv) >= 3:
        ipDir = sys.argv[1]
        prefix = sys.argv[2]
        getFourthSNP(ipDir, prefix)
    else:
        print 'err: '
                
if __name__=='__main__':
    main()
