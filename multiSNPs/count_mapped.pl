# ! /usr/local/bin/perl

#open fil, "<",  "/scratch/uv1000/huws/mohit/bgicomp/data/streptoFasta/strepto/Sample_A7_Unique.sam";
open fil, "<",   $ARGV[0];
open writ, ">", $ARGV[0].".Otherlines.txt";
open writ1, ">", $ARGV[0].".Perfect2.txt";
open writ2, ">", $ARGV[0].".Multiple2.txt";
$a=0; $b=0;$d=0; $e=0;$t=0;$w=0;
while($record=<fil>){
 $w=$w+1; 
 if($record=~ m/^HWI/){
	$t=$t+1;
	@c=split(/\t/,$record);
        if($c[1]==4){
	    #unmapped
	    $a=$a+1;
        }
        elsif($c[1]==16){
	    #reverse
	    $b=$b+1;
	    print writ2 $record;
        }
        elsif($c[1]==0){
	    #forward
	    $e=$e+1;
	    print writ1 $record;
        }
	else{
	    $d=$d+1;
               
        }

}
else{
	print writ $record;
}
}
print $ARGV[0], "\n";
print $a, "-4","*****", $b, "-16", "*******", $e,"-0","*****",$d,"-else","*******",$t,"-HWI","******",$w,"\n";

