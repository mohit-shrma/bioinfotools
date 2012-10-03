#!/usr/bin/perl   # add -Tw to force taint checks, and print warnings

##############################################################################
# Copyright: (c) 2011 Terk Shuen Lee
# All Rights Reserved.
#
# Convert MUMMER coords output to tab-delimited file. (-rcl options in show-coords)
# Split values using whitespace, INSTEAD of fixed column widths,
# because columns with >8 digits will be expanded and thus give wrong values with "unpack".
# 
# Read fasta file from stdin, Ouput to stdout.
#
# Default nucmer format:
#    [S1]     [E1]  |     [S2]     [E2]  |  [LEN 1]  [LEN 2]  |  [% IDY]  |  [LEN R]  [LEN Q]  |  [COV R]  [COV Q]  | [TAGS]
#===============================================================================================================================
#      21     6528  |     6508        1  |     6508     6508  |   100.00  |     7378     6508  |    88.21   100.00  | gi|342367752|gb|AFTD01265786.1|	AABSBUcontig_29791
#    6540     7361  |        1      822  |      822      822  |    99.76  |     7378      822  |    11.14   100.00  | gi|342367752|gb|AFTD01265786.1|	AALZQQcontig_210669
##############################################################################

use strict;
use warnings;

$|++; # force auto flush of output buffer

#processes
sub main {
  load();
}

#load fasta file
sub load() {  
  <>; #skip first 5 lines
  <>;
  <>;
  <>;
  <>;

  my @cols;
  while(<>) { #read from stdin

    #chomp; #no need, newline is considered as whitespace and will be removed by split
    #@cols = unpack("A8xA8x3A9xA8x3A9xA8x3A9x3A9xA8x3A9xA8x3A*",$_); #old method using fixed col width
    
    @cols = split(); #split on whitespace in $_, removing leading whitespace and newline at the end
    print "$cols[0]\t$cols[1]\t$cols[3]\t$cols[4]\t$cols[6]\t$cols[7]\t$cols[9]\t$cols[11]\t$cols[12]".
          "\t$cols[14]\t$cols[15]\t$cols[17]\t$cols[18]\n";

  }
}

main();
