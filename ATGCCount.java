import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.DataInputStream;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;


public class ATGCCount {
	
	private String inputFile;
	private String outputFile;
	
	public ATGCCount(String inputFile, String outputFile) {
		this.inputFile = inputFile;
		this.outputFile = outputFile;
	}
	
	private void doCount() {
		
		FileInputStream ipFstream = null;
		FileWriter opFstream = null;
		
		DataInputStream in = null;
		BufferedReader br = null;
		BufferedWriter bw = null;
		
		try {
			
			ipFstream = new FileInputStream(inputFile);
			opFstream = new FileWriter(outputFile);
			
			//prepare input for read
		    in = new DataInputStream(ipFstream);
		    br = new BufferedReader(new InputStreamReader(in));
		    
		    //prepare output for write
		    bw = new BufferedWriter(opFstream);
		    
		    String strLine = br.readLine();
		    int ACount = -1;
		    int TCount = -1;
		    int GCount = -1;
		    int CCount = -1;
		    int NCount = -1;
		    bw.write("name\tA\tT\tG\tC\tN\n");
		    while (strLine != null && strLine.length() > 0) {
		    	if (strLine.startsWith(">")) {
		    		//got the header
		    		//output previous counts
		    		if (ACount != -1) {
		    			bw.write(ACount+"\t");
			    		bw.write(TCount+"\t");
			    		bw.write(GCount+"\t");
			    		bw.write(CCount+"\t");
			    		bw.write(NCount+"\n");
		    		}
		    		//output the new header
		    		bw.write(strLine.substring(1)+"\t");
		    		//reset all counts
		    		ACount = 0;
		    		TCount = 0;
		    		GCount = 0;
		    		CCount = 0;
		    		NCount = 0;
		    	} else {
		    		//update counts from new line
		    		for (int i =0; i < strLine.length(); i++) {
		    			if (strLine.charAt(i) =='A') {
		    				++ACount;
		    			} if (strLine.charAt(i) =='T') {
		    				++TCount;
		    			} if (strLine.charAt(i) =='G') {
		    				++GCount;
		    			} if (strLine.charAt(i) =='C') {
		    				++CCount;
		    			} if (strLine.charAt(i) =='N') {
		    				++NCount;
		    			}
		    		}
		    	}
		    	strLine = br.readLine();
		    }
		    
		    //output corresponding to last header
		    if (ACount != -1) {
    			bw.write(ACount+"\t");
	    		bw.write(TCount+"\t");
	    		bw.write(GCount+"\t");
	    		bw.write(CCount+"\t");
	    		bw.write(NCount+"\n");
    		}
			
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} finally {
			try {
				
				bw.flush();
				bw.close();
				in.close();
				br.close();
				opFstream.close();
				ipFstream.close();
			} catch (IOException e) {
				e.printStackTrace();
			}
			
		}
		
	}
	
	public void startCounting() {
		doCount();
	}
	
	public static void main(String[] args) {
		String inputFile = args[0];
		String outFile = args[1];
		System.out.println(args.length);
		System.out.println(args[0]);
		System.out.println(args[1]);
		System.out.println(args[2]);
		//ATGCCount counter = new ATGCCount(inputFile, outFile);
		//counter.doCount();
	}
	
}