#! /usr/local/bin/perl

#this script pull out unique reads and repeated reads, with their counts


open fil, "<", $ARGV[0];     #open fil, "<","SRR329954_1.sam";
open uniqFile, ">", $ARGV[1];    #open uniqFile, ">","SRR329954_1_Unique.sam";
open infoFile, ">", $ARGV[2];   #open infoFile, ">","SRR329954_1_info.txt";
#open repFile, ">", $ARGV[3];   #this is for repeats

$i=0;
$U=0;
$R=0;
$N=0;

while ($record=<fil>){
    chomp($record);

    $i=$i+1;
    if($i<=1) {
	print uniqFile $record, "\n";
    }

    if($record=~/XT:A/) {
	@c=split("\t",$record);
	$a=$c[11];
	@d=split(":",$a);
	if($d[2] eq "U") {
	    $U=$U+1;
	    print uniqFile $record, "\n";
	}
	elsif($d[2] eq "R") {
	    $R=$R+1;
	    #print repFile $record, "\n";
	}
	else {
	    $N=$N+1;
	}
    }
}

print infoFile "Unique count: ", $U, "\n";
print infoFile "Repeat count: ", $R, "\n";
print infoFile "N count: ", $N, "\n";

#print $U;
