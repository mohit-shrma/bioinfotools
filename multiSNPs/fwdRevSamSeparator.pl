# ! /usr/local/bin/perl

#Example to run program: perl ~/programs/fwdRwvSamSeparator.pl Sample_A10.sam


#open the sam file to work on
#open samFile, "<",  "/scratch/uv1000/huws/mohit/bgicomp/data/streptoFasta/strepto/Sample_A7_Unique.sam";
open samFile, "<",   $ARGV[0];

#forward sam file to write to
open fwdSam, ">", "Fwd".$ARGV[0];

#reverse sam file to write to
open revSam, ">", "Rev".$ARGV[0];

$unmappedCount = 0;
$revCount = 0;
$otherCount = 0;
$fwdCount = 0;
$validRecordCount = 0;
$totalRecordCount = 0;

while($record=<samFile>)
{
    #get the next record in file
    $totalRecordCount = $totalRecordCount + 1;
    
    if($record=~ m/^HWI/)
    {
	#record is a vaild record
	
	$validRecordCount = $validRecordCount + 1;

	@c=split(/\t/,$record);
	
        if($c[1]==4)
	{
	    #unmapped
	    $unmappedCount = $unmappedCount + 1;
        }
        elsif($c[1]==16)
	{
	    #reverse
	    $revCount = $revCount + 1;
	    print revSam $record;
        }
        elsif($c[1]==0)
	{
	    #forward
	    $fwdCount = $fwdCount + 1;
	    print fwdSam $record;
        }
	else
	{
	    $otherCount = $otherCount + 1;
        }
    }
    else
    {
	print writ $record;
    }
}


print "Unmapped count: ", $unmappedCount, "\n";
print "Reverse count: ", $revCount, "\n";
print "Forward count: ", $fwdCount, "\n";
print "Other count: ", $otherCount, "\n";
print "Valid record count: ", $validRecordCount, "\n";
print "Total record count: ", $totalRecordCount, "\n";
