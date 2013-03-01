import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.Vector;

import au.com.bytecode.opencsv.CSVReader;

import com.beust.jcommander.JCommander;
import com.interval.IntervalNode;
import com.interval.IntervalTree;
import com.lastzout.LastzOutputParser;
import com.redblack.*;

/*
 * -lastzOutDir /Users/mohit/Documents/hugroup/koronis/June13RelaxLastzRefNCGR/June13LastzOut  
 * -output /Users/mohit/Documents/hugroup/koronis/June13RelaxLastzRefNCGR/June13LastzOut/NCGRRefRelaxStats75K.txt  
 * -minMatchLen 75000
 */

/*
 * -lastzOutDir //Users/mohit/Documents/hugroup/koronis/July11LastzBGIRef/lastzOut  
 * -output /Users/mohit/Documents/hugroup/koronis/July11LastzBGIRef/coverageStats.txt  
 * -minMatchLen 5000
 */

class RedBlackMain {
	
	private RedBlackTree redBlackTree;
	private IntervalTree intervalTree;
	
	private static final int GENE_MAP_SCAFFID_COL = 1;
	private static final int GENE_MAP_START_COL = 4;
	private static final int GENE_MAP_END_COL = 5;
	private static final int GENE_MAP_TYPE_COL = 2;
	private static final int GENE_MAP_FEAT_SYMB_COL = 6;
	
	private static final String SCAFF_EXT= "fasta";
	private static final String OUT_EXT= "out";
	
	private static final int LASTZ_START_COL = 4;
	private static final int LASTZ_END_COL = 5;
	private static final int LASTZ_QNAME_COL = 6;
	private static final int LASTZ_SIZE_COL = 3;
	
	public RedBlackMain() {
		redBlackTree = new RedBlackTree();
		intervalTree = new IntervalTree();
	}
	
	public void insertNewRBNode(int key) {
		redBlackTree.insert(new RedBlackNode(key));
	}
	
	public void insertNewIntvNode(int low, int high) {
		intervalTree.insert(new IntervalNode(low, high));
	}
	
	public void rbInorder() {
		redBlackTree.inorderTreeWalk(redBlackTree.getRoot());
	}
	
	public void rbLevelOrder() {
		redBlackTree.levelOrderWalk(redBlackTree.getRoot());
	}
	
	public void intervalInorder() {
		intervalTree.inorderTreeWalk(intervalTree.getRoot());
	}
	
	public void intervalLevelOrder() {
		intervalTree.levelOrderWalk(intervalTree.getRoot());
	}
	
	public void queryOverlapInterval(int low, int high) {
		IntervalNode result = (IntervalNode) intervalTree.intervalSearch(
													new IntervalNode(low, high));
		if (result != intervalTree.getLeaf()) {
			System.out.println(result.getKey() +"\t"
								+ (result).getHigh() + "\t"
								+ (result).getMaxHi() + "\t"
								+ result.getColor() + "\t"
								+ intervalTree.getBlackHeight(result)
								);
		} else {
			System.out.println("no results found");
		}
	}
	
	public void printMergedWalk() {
		Vector<IntervalNode> mergedWalkNodeStack = new Vector<IntervalNode>();
		intervalTree.inOrderMergedWalk((IntervalNode) intervalTree.getRoot(), 
										mergedWalkNodeStack);
		for (IntervalNode  intervalNode : mergedWalkNodeStack) {
			System.out.println(intervalNode.getLow() + ", " 
								+ intervalNode.getHigh());
		}
	}
	
	public void countGaps(int start, int end) {
		int gapCount = intervalTree.countGaps(start, end);
		System.out.println("Number of gaps: " + gapCount);
	}
	
	public void processFile(String fileName) {
		LastzOutputParser lastzOutputParser = new LastzOutputParser(fileName,
																0,
																LASTZ_START_COL, 
																LASTZ_END_COL, 
																LASTZ_QNAME_COL, 
																LASTZ_SIZE_COL);
		lastzOutputParser.parse();
		//lastzOutputParser.printMergedWalk();
		
		for (String scaffold : lastzOutputParser.getScaffolds()) {
			System.out.print(scaffold+", ");
		}
		System.out.println("");
		System.out.println("ref. scaffold size : "
							+ lastzOutputParser.getReferenceScaffoldSize());
		System.out.println("Gaps count: "+lastzOutputParser.countGaps());
	}
	
	
	
	public void countGeneMappings(String dirName, 
									String geneMapFileName,
									String outputFileName,
									int minMatchLen) {
		
		File dir = new File(dirName);
		LastzOutputParser lastzOutputParser = null;
		
		HashMap<String, Boolean> geneCovered = new HashMap<String, Boolean>();
		HashSet<String> geneLost = new HashSet<String>();
		HashSet<String> allGeneSymbol = new HashSet<String>();
		
		int geneSymbolsCoveredCount = 0;
		int geneSymbolsNotCoveredCount = 0;
		
		try {
			CSVReader geneMapReader = new CSVReader(
										new FileReader(geneMapFileName), '\t');
			//read the header
			String[] line = geneMapReader.readNext();
			
			//current scaffold being operated
			String currScaffName = "";
			String newScaffName = "";
			int geneStart = -1;
			int geneEnd = -1;
			int geneLength = -1;
			int unMatchedLen = -1;
			int matchedLen = -1;
			float pcMatchedLen = 0;
			boolean isGeneCovered = false;
			String geneType = "";
			String geneSymbol = "";
			String scaffFileName = "";
			File scaffOutFile = null;
			
			/*open file to record EST/gene type, geneFeatureSymbol, 
				its length and length matched in high confidence region
			*/
			FileOutputStream fos3 = new FileOutputStream(outputFileName 
					+ "HiConfStats");
			BufferedOutputStream bos3 = new BufferedOutputStream(fos3);
			bos3.write(("GeneType\tGeneFeatureSymbol\tLength"+
								"\tLengthInHiConf\tpcMatchedLen\n").getBytes());
			
			
			while ((line = geneMapReader.readNext()) != null 
						&& line.length > 1) {
				
				newScaffName = line[GENE_MAP_SCAFFID_COL];
				geneStart = Integer.parseInt(line[GENE_MAP_START_COL]);
				geneEnd = Integer.parseInt(line[GENE_MAP_END_COL]);
				geneType = line[GENE_MAP_TYPE_COL];
				geneSymbol = line[GENE_MAP_FEAT_SYMB_COL];
				geneLength = geneEnd - geneStart + 1;
				
				allGeneSymbol.add(geneSymbol);
				
				if (!newScaffName.equalsIgnoreCase(currScaffName)) {
					//got a new scaffold, read the scaffold outputfile
					//from directory
					lastzOutputParser = null;
					scaffFileName = dir.getCanonicalPath() + File.separatorChar
									+ newScaffName + "." + SCAFF_EXT + "." 
									+ OUT_EXT;
					scaffOutFile = new File(scaffFileName);
					if (scaffOutFile.exists()) {
						lastzOutputParser = new LastzOutputParser(
								scaffOutFile.getCanonicalPath(),
								0,
								LASTZ_START_COL, 
								LASTZ_END_COL, 
								LASTZ_QNAME_COL, 
								LASTZ_SIZE_COL);
						lastzOutputParser.parse();
					} else {
						//scaffold output file not found
						geneLost.add(geneSymbol);
						continue;
					}
					
					currScaffName = newScaffName;
				} else {
					//same scaffold as previous, no need to read scaffold file 
					//from dir
				}
				
				
				//check for the conflict of interval [start, end] in current
				//scaffold interval tree
				if (null != lastzOutputParser) {
					isGeneCovered = lastzOutputParser.isCompletelyCovered(
															geneStart, 
															geneEnd, 
															minMatchLen);
					
					if (!geneCovered.containsKey(geneSymbol) || 
							geneCovered.get(geneSymbol)) {
						//if gene symbol is not present in dict or if previous
						//value of gene coverage is True
						geneCovered.put(geneSymbol, isGeneCovered);
					}
					
					
					/*record EST/gene type, geneFeatureSymbol, 
					its length and length matched in high confidence region
					*/
					unMatchedLen = lastzOutputParser.getIntervalNonCoverage(
															geneStart, geneEnd);
					matchedLen =  geneLength - unMatchedLen;
					pcMatchedLen = ((float)matchedLen)/geneLength *100;
					bos3.write((geneType + '\t' + geneSymbol + '\t' 
								+ geneLength + '\t' + matchedLen + '\t' 
								+ pcMatchedLen + '\n').getBytes());
					
				}
				
			}
			
			System.out.println("Total gene symbols: " + allGeneSymbol.size());
			
			System.out.println("Total gene symbols found in scaffs: " + geneCovered.size());
			System.out.println("Lost genes in not included scaffs: " + geneLost.size());
			
			//remove gene symbols not found from geneCovered set
			//Set<String> difference = new HashSet<String>(geneCovered.keySet());
			geneCovered.keySet().removeAll(geneLost);
			
			System.out.println("Total gene symbols in scaffs excluding lost ones: "
										+ geneCovered.size());
			//System.out.println("Lost gene in scaffs: " + geneLost.size());
			
			
			FileOutputStream fos = new FileOutputStream(outputFileName);;
			BufferedOutputStream bos = new BufferedOutputStream(fos);
			bos.write(("GeneType\tGeneFeatureSymbol\n").getBytes());
			
			FileOutputStream fos2 = new FileOutputStream(outputFileName 
																	+ "NonCov");
			BufferedOutputStream bos2 = new BufferedOutputStream(fos2);
			bos2.write(("GeneType\tGeneFeatureSymbol\n").getBytes());
			
			//parse the hash map gene covered and print only those who are true
			for (Map.Entry<String, Boolean> entry : geneCovered.entrySet()) {
			    String geneSymbolKey = entry.getKey();
			    Boolean isGeneSymCovered = entry.getValue();
			    if (isGeneSymCovered) {
			    	bos.write((geneType + '\t' +geneSymbolKey + '\n').getBytes());
			    	geneSymbolsCoveredCount++;
			    } else {
			    	bos2.write((geneType + '\t' +geneSymbolKey + '\n').getBytes());
			    	geneSymbolsNotCoveredCount++;
			    }
			}
			
			System.out.println("Gene symbols completely covered: " 
								+ geneSymbolsCoveredCount);
			
			System.out.println("Gene symbols not completely covered: " 
								+ geneSymbolsNotCoveredCount);	
			
			bos.flush();

			if (bos != null) {
				try {
					bos.close();
				} catch (IOException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}
			
			if (fos != null) {
				try {
					fos.close();
				} catch (IOException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}
			
			bos2.flush();

			if (bos2 != null) {
				try {
					bos2.close();
				} catch (IOException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}
			
			if (fos2 != null) {
				try {
					fos2.close();
				} catch (IOException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}
			
			bos3.flush();
			
			if (bos3 != null) {
				try {
					bos3.close();
				} catch (IOException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}
			
			if (fos3 != null) {
				try {
					fos3.close();
				} catch (IOException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}
			
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	public void processDir(String dirname, String outputFileName, 
							int minMatchLen) {
		
		File dir = new File(dirname);
		File[] files = dir.listFiles();
		
		LastzOutputParser lastzOutputParser = null;
		
		FileOutputStream fos = null;
		BufferedOutputStream bos = null;
		try {
			fos = new FileOutputStream(outputFileName);
			bos = new BufferedOutputStream(fos);
		} catch (FileNotFoundException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}
		
		try {
			bos.write(("Name\tSize\tGaps\tNumScaff\tScaffolds\tPcMapped\tmacthedLen\n").getBytes());
		} catch (IOException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}
		
		String tempName = "";
		String size = "";
		String countgaps = "";
		String mappedPc ="";
		String numScaffolds = "";
		String scaffoldsName = "";
		String matchedLen = "";
		
		for (File file : files) {
			if (file.getAbsolutePath().endsWith("fasta.out")) {
				try {
					lastzOutputParser = new LastzOutputParser(file.getCanonicalPath(),
																minMatchLen, 
																LASTZ_START_COL, 
																LASTZ_END_COL, 
																LASTZ_QNAME_COL, 
																LASTZ_SIZE_COL);
					lastzOutputParser.parse();
					
					tempName = file.getName().substring(0, 8);
					size = lastzOutputParser.getReferenceScaffoldSize() + "";
					countgaps = lastzOutputParser.countGaps() +"";
					
					float mapped_pc = 0;
					if (lastzOutputParser.getReferenceScaffoldSize() > 0) {
						mapped_pc  = 100 * (((float)(lastzOutputParser.getReferenceScaffoldSize() 
								- lastzOutputParser.countGaps()) )
								/ lastzOutputParser.getReferenceScaffoldSize());
					}
					
					mappedPc = mapped_pc +"";
					numScaffolds = "" + lastzOutputParser.getScaffolds().size();
					scaffoldsName = "";
					for (String scaffold : lastzOutputParser.getScaffolds()) {
						if (scaffoldsName.length() != 0) {
							scaffoldsName += '|';
						}
						scaffoldsName += scaffold;
					}
					
					matchedLen = lastzOutputParser.getMatchedLength();
					
					bos.write((tempName+"\t"+size+"\t"+countgaps+"\t"+
								numScaffolds+"\t"+scaffoldsName+"\t"+
								mappedPc+"\t"+matchedLen+"\n").getBytes());
					bos.flush();
				} catch (IOException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				} 
				
			}
		}
		
		if (bos != null) {
			try {
				bos.close();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
		
		if (fos != null) {
			try {
				fos.close();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
		
	}
	
	public static void main(String[] args) {
		
		RedBlackMain obj = new RedBlackMain();
		String dirName = "";
		String opFileName = "";
		String geneMapFileName = "";
		int minMatchLen = -1;

		if (args.length < 1) {
			System.out.println("this program takes commandline arguments");
		}
		
		RBArgs  rbArgs = new RBArgs();
		new JCommander(rbArgs, args);

		dirName = rbArgs.lastzOutDir;
		opFileName = rbArgs.output;
		minMatchLen = rbArgs.minMatchLen.intValue();
		
		if (!rbArgs.geneCoverage) {
			/*
			 * -lastzOutDir /Users/mohit/Documents/hugroup/koronis/June13RelaxLastzRefNCGR/June13LastzOut  
			 * -output /Users/mohit/Documents/hugroup/koronis/June13RelaxLastzRefNCGR/June13LastzOut/NCGRRefRelaxStats75K.txt  
			 * -minMatchLen 75000
			 */

			obj.processDir(dirName, opFileName, minMatchLen);
		} else {
			/*
			 * takes dir containining all lastz outputs, filename to putput the results to
			 * -lastzOutDir //Users/mohit/Documents/hugroup/koronis/June13RelaxLastzRefNCGR/June13LastzOut  
			 * -output /Users/mohit/Documents/hugroup/koronis/June13RelaxLastzRefNCGR/coverage900Stats.txt  
			 * -minMatchLen 900 
			 * -geneMapFile /Users/mohit/Documents/hugroup/koronis/geneMap/NCGRGeneMap.txt
			 */
			/*takes dir containing all fasta.outs(lastz o/p), gene annotation file,
			 * filename to output to 
			 * /Users/mohit/Documents/hugroup/koronis/June13RelaxLastzRefNCGR/June13LastzOut
			 * /Users/mohit/Documents/hugroup/koronis/geneMapOut.txt
			 * /Users/mohit/Documents/hugroup/koronis/NCGRGeneMap.txt  
			 * 
			 * 
			 * 
			 */
			geneMapFileName = rbArgs.geneMapFile;
			obj.countGeneMappings(dirName, geneMapFileName, opFileName, minMatchLen);
		}
	}
	
}