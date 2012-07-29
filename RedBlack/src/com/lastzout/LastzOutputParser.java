package com.lastzout;

import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashMap;
import java.util.Vector;

import au.com.bytecode.opencsv.CSVReader;

import com.interval.IntervalNode;
import com.interval.IntervalTree;

public class LastzOutputParser {
	
	private IntervalTree intervalTree;
	private Vector<String> scaffoldNames;
	private Vector<String> scaffoldNamesStrength;
	private String fileName;
	private int startCol;
	private int endCol;
	private int nameCol;
	private int sizeScaffoldCol;
	private int sizeScaffold;
	private int minMatchLen;
	
	//"", 4, 5, 1, 3 
	public LastzOutputParser(String fileName, 
								int minMatchLen, int startCol, int endCol,
								int nameCol, int sizeScaffoldCol) {
		this.fileName = fileName;
		this.startCol = startCol;
		this.endCol = endCol;
		this.nameCol = nameCol;
		this.sizeScaffoldCol = sizeScaffoldCol;
		this.minMatchLen = minMatchLen;
	}
	
	public void parse() {
		try {
			
			CSVReader reader = new CSVReader(
										new FileReader(fileName), '\t');
			//read the header
			String line[] = reader.readNext();
			
			intervalTree = new IntervalTree();
			scaffoldNames = new Vector<String>();
			String tempName = "";
			int start = -1;
			int end = -1;
			while ((line = reader.readNext()) != null) {
				
				tempName = line[nameCol];
				start = Integer.parseInt(line[startCol]);
				end = Integer.parseInt(line[endCol]);
				
				if ((end - start + 1) < minMatchLen) {
					continue;
				}
				
				intervalTree.insert(new IntervalNode(start, end, tempName));
				
				if (scaffoldNames.isEmpty()) {
					scaffoldNames.add(tempName);
					sizeScaffold = Integer.parseInt(line[sizeScaffoldCol]);
				} else if (!scaffoldNames.lastElement().equalsIgnoreCase(tempName)) {
					scaffoldNames.add(tempName);
				}
				
			}
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
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
	
	public void printInorderLengthWalk() {
		Vector<IntervalNode> nodeStack = new Vector<IntervalNode>();
		intervalTree.inOrderWalk((IntervalNode) intervalTree.getRoot(), 
									nodeStack);
		for (IntervalNode intervalNode: nodeStack) {
			System.out.println(intervalNode.getScaffName() + ":" + 
								(intervalNode.getHigh()-intervalNode.getLow()));
		}
	}
	
	//TODO: cleanup code below bad hard code
	private HashMap<String, Vector> getInorderLengthWalk() {
		HashMap<String, Vector> hMap = new HashMap<String, Vector>(10); 
		Vector<IntervalNode> nodeStack = new Vector<IntervalNode>();
		intervalTree.inOrderWalk(intervalTree.getRoot(), 
									nodeStack);
		int matchLenTillNow = -1, matchedLength = -1, lo = -1, hi = -1;
		String scaffName = "";
		Vector loHiMatchLen = null;
		for (IntervalNode intervalNode: nodeStack) {
			matchedLength = intervalNode.getHigh()-intervalNode.getLow();
			scaffName = intervalNode.getScaffName();
			
			if (hMap.containsKey(scaffName)) {
				//Vector loHiMatchLen = new Vector(3);
				loHiMatchLen = hMap.get(scaffName);
				lo = (Integer) loHiMatchLen.elementAt(0);
				hi = (Integer) loHiMatchLen.elementAt(1);
				matchLenTillNow = (Integer) loHiMatchLen.elementAt(2);
				
				//check for overlap
				if (!(lo > intervalNode.getHigh() || 
						hi < intervalNode.getLow())) {
					System.out.println("ovr lap");
					if (intervalNode.getLow() >= lo && 
							intervalNode.getLow() <= hi) {
						//if new low is between
						matchedLength = intervalNode.getHigh() - hi;
						if (matchedLength > 0) {
							matchLenTillNow += matchedLength;
							hi = intervalNode.getHigh();
						}
					}else if (intervalNode.getHigh() <= hi &&
								intervalNode.getHigh() >= lo) {
						//if new high is between
						System.out.println("hi");
						matchedLength = lo - intervalNode.getLow();
						if (matchedLength > 0) {
							matchLenTillNow += matchedLength;
							lo = intervalNode.getLow();
						}
					} else if (intervalNode.getLow() < lo 
							&& intervalNode.getHigh() > hi) {
						//newlo < lo and newhi > hi
						System.out.println("b/w");
						matchLenTillNow = intervalNode.getHigh() - 
												intervalNode.getLow();
						lo = intervalNode.getLow();
						hi = intervalNode.getHigh();
					} else {
						System.out.println("err");
					}
				} else {
					//no overlap
					matchedLength = intervalNode.getHigh() - 
											intervalNode.getLow();
					lo = intervalNode.getLow()<lo?intervalNode.getLow():lo;
					hi = intervalNode.getHigh()>hi?intervalNode.getHigh():hi;
					matchLenTillNow += matchedLength;
				}
				loHiMatchLen.setElementAt(lo, 0);
				loHiMatchLen.setElementAt(hi, 1);
				loHiMatchLen.setElementAt(matchLenTillNow, 2);
				hMap.put(scaffName, loHiMatchLen);
			} else {
				lo = intervalNode.getLow();
				hi = intervalNode.getHigh();
				matchLenTillNow = hi - lo;
				loHiMatchLen = new Vector(3);
				loHiMatchLen.add(0, lo);
				loHiMatchLen.add(1, hi);
				loHiMatchLen.add(2, matchLenTillNow);
				hMap.put(scaffName, loHiMatchLen);
			}
		}
		return hMap;
	}
	
	public String getMatchedLength() {
		HashMap<String, Vector> hMap = getInorderLengthWalk();
		String str = "";
		StringBuffer strBuff = new StringBuffer();
		for (String scaffName : hMap.keySet()) {
			int matchLen = (Integer) hMap.get(scaffName).elementAt(2);
			strBuff.append(scaffName+":"+matchLen+","); 
		}
		str = strBuff.toString();
		if (str.endsWith(",")) {
			str = str.substring(0, str.length()-1);
		}
		return str;
	}
	
	
	public boolean isCompletelyCovered(int start, int end, int minMatchLen) {
		return intervalTree.isRegionFullyCovered(new IntervalNode(start, end), 
													minMatchLen);
	}
	
	public int getIntervalNonCoverage(int start, int end) {
		int unMatchedLen = intervalTree.getIntervalNotCovered(
											new IntervalNode(start, end));
		return unMatchedLen;
	}
	
	//TODO
	public int countGaps() {
		int gapCount = intervalTree.countGaps(0, sizeScaffold);
		return gapCount;
	}
	
	public Vector<String> getScaffolds() {
		return scaffoldNames;
	}
	
	public int getReferenceScaffoldSize() {
		return sizeScaffold;
	}
	
	
	
}
