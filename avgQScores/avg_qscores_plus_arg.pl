#! /user/local/bin/perl



if ($#ARGV != 3) {
    print "usage: \n";
    exit;
}



#open INPUT1, "<", "/project/huws/huwsgroup/BacteriaSequenceErnie/from_colorado/Project_Ernie_Retzl_Streptomyces_pool_1/Sample_A1/A1_ATCACG_L008_R1_001.fastq";
#open INPUT2, "<", "/project/huws/huwsgroup/BacteriaSequenceErnie/from_colorado/quality_scores_1.8+.txt"; #look in Bayer folder for Illumina 1.3+ quality score file
#open OUTPUT1, ">", "/project/huws/huwsgroup/BacteriaSequenceErnie/from_colorado/Project_Ernie_Retzl_Streptomyces_pool_1/Sample_A1/A1_ATCACG_L008_R1_001_seqavgs.txt";
#open OUTPUT2, ">", "/project/huws/huwsgroup/BacteriaSequenceErnie/from_colorado/Project_Ernie_Retzl_Streptomyces_pool_1/Sample_A1/A1_ATCACG_L008_R1_001_avgscore.txt";

open INPUT1, "<", $ARGV[0];
open INPUT2, "<", $ARGV[1]; #look in Bayer folder for Illumina 1.3+ quality score file
open OUTPUT1, ">", $ARGV[2];
open OUTPUT2, ">", $ARGV[3];

$max = 16000000; #number of lines in fastq file
$no_seq = $max/4;#number of sequences in fastq file

%scores = ();
@table = <INPUT2>;
chomp @table;
close INPUT2;

foreach $row (@table) { #read table of ASCII-to-Phred conversion into an array
        @entries = split(/\t/,$row);
        $symbol = $entries[1];
        $scores{$symbol} = $entries[2]; #make a hash table with ASCII character as key and Phred score as value
}

@seq = ((0) x 50); #initialize array for computing sequence average scores; assumes 50bp reads

%sums = (); #initialize hash table for computing position average scores

$k = 0;
for ($k=0; $k<50; $k++) { #again assumed 50bp reads
	$id = $k;
	$sums{$id} = 0;
}

$i = 0; #index for moving through fastq file

while ($record = <INPUT1>) {

        $i++; #increment line number, starting with 1

        if ( $i%4 == 0 ) { #look only at quality score line of fastq file

                chomp $record;
                @qscores = split(//,$record);
		
                $seq_total = 0;
		$j = 0;

                foreach $letter (@qscores) {

                        $num = $scores{$letter};
                        $seq_total = $seq_total + $num; #add to total for the sequence

			$sums{$j} = $sums{$j} + $num; #add to total for the position
			$j++; #increment to next position in the sums hash

		}

		$seq_avg = $seq_total/50; #again assumed 50bp read
		print OUTPUT1 $seq_avg, "\n";

	}

}

close INPUT1;

while(($key, $value) = each(%sums)) {
	$avg = $value/$no_seq;
	print OUTPUT2 "$key", "\t", "$avg", "\n";
}

close OUTPUT2;
