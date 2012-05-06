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
	
	//"", 4, 5, 1, 3 
	public LastzOutputParser(String fileName, int startCol, int endCol,
								int nameCol, int sizeScaffoldCol) {
		this.fileName = fileName;
		this.startCol = startCol;
		this.endCol = endCol;
		this.nameCol = nameCol;
		this.sizeScaffoldCol = sizeScaffoldCol;
	}
	
	public void parse() {
		try {
			
			CSVReader reader = new CSVReader(
										new FileReader(fileName), '\t');
			
			String line[] = reader.readNext();
			
			intervalTree = new IntervalTree();
			scaffoldNames = new Vector<String>();
			String tempName = "";
			while ((line = reader.readNext()) != null) {
				tempName = line[nameCol];
				intervalTree.insert(new IntervalNode(
											Integer.parseInt(line[startCol]), 
											Integer.parseInt(line[endCol]),
											tempName));
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
	
	private HashMap<String, Integer> getInorderLengthWalk() {
		HashMap<String, Integer> hMap = new HashMap<String, Integer>(10); 
		Vector<IntervalNode> nodeStack = new Vector<IntervalNode>();
		intervalTree.inOrderWalk(intervalTree.getRoot(), 
									nodeStack);
		int matchedLength = -1;
		String scaffName = "";
		for (IntervalNode intervalNode: nodeStack) {
			matchedLength = intervalNode.getHigh()-intervalNode.getLow();
			scaffName = intervalNode.getScaffName();
			if (hMap.containsKey(scaffName)) {
				hMap.put(scaffName, hMap.get(scaffName) + matchedLength);
			} else {
				hMap.put(scaffName,matchedLength);
			}
		}
		return hMap;
	}
	
	public String getMatchedLength() {
		HashMap<String, Integer> hMap = getInorderLengthWalk();
		String str = "";
		StringBuffer strBuff = new StringBuffer();
		for (String scaffName : hMap.keySet()) {
			int matchLen = hMap.get(scaffName);
			strBuff.append(scaffName+":"+matchLen+","); 
		}
		str = strBuff.toString();
		if (str.endsWith(",")) {
			str = str.substring(0, str.length()-1);
		}
		return str;
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
