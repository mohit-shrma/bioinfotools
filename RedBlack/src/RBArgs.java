
import com.beust.jcommander.Parameter;

public class RBArgs {
	
    @Parameter(names = "-lastzOutDir", description = "dir containing lastz outputs for scaffolds")
    public String lastzOutDir;
    
    @Parameter(names = "-output", description = "file to write output to")
    public String output;
    
    @Parameter(names = "-minMatchLen", description = "minimum match length to filter")
    public Integer minMatchLen;

    @Parameter(names = "-geneMapFile", description = "gene annotation file for the genome")
    public String geneMapFile;
    
    @Parameter(names = "-geneCoverage", description = "whether to compute gene coverage or scaff coverage stats")
    public boolean geneCoverage = false;
	
}