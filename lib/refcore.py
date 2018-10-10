from __future__ import print_function
#############################################################################
# Referee CORE functions
# Gregg Thomas
# August 2013-present
# Forked from core on 12.13.2015
# Updated for Referee October 2018
#############################################################################

import sys, os, timeit, datetime, time, gzip, string, random

#############################################################################

def errorOut(errnum, errmsg, globs):
# Formatting for error messages.
	fullmsg = "|**Error " + str(errnum) + ": " + errmsg + " |";
	border = " " + "-" * (len(fullmsg)-2);
	fullstr = "\n" + border + "\n" + fullmsg + "\n" + border + "\n"
	printWrite(globs['logfilename'], globs['log-v'], "\n" + border + "\n" + fullmsg + "\n" + border + "\n")
	endProg(globs);

#############################################################################

def startProg(globs):
# A nice way to start the program.
	print("#");
	printWrite(globs['logfilename'], globs['log-v'], "# =================================================");
	print(welcome());
	print("    Reference genome quality score calculator.\n")
	printWrite(globs['logfilename'], 0, "# Welcome to Referee -- Reference genome quality score calculator.");
	printWrite(globs['logfilename'], globs['log-v'], "# The date and time at the start is: " + getDateTime());
	printWrite(globs['logfilename'], globs['log-v'], "# The program was called as: " + " ".join(sys.argv));
	printWrite(globs['logfilename'], globs['log-v'], "#\n# " + "-" * 40 + "\n#");
	printWrite(globs['logfilename'], globs['log-v'], "** IMPORTANT!");
	printWrite(globs['logfilename'], globs['log-v'], "** Input columns: Scaffold\tPosition\tAA\tAC\tAG\tAT\tCC\tCG\tCT\tGG\tGT\tTT");
	printWrite(globs['logfilename'], globs['log-v'], "** Please ensure that your input genotype likelihood files are tab delimited with columns in this exact order without headers.");
	printWrite(globs['logfilename'], globs['log-v'], "** Failure to do so will result in inaccurate calculations!!");
	printWrite(globs['logfilename'], globs['log-v'], "#\n# " + "-" * 40 + "\n#");

	if globs['fastq']:
		printWrite(globs['logfilename'], globs['log-v'], "# --fastq : Output format is FASTQ.");
	else:
		printWrite(globs['logfilename'], globs['log-v'], "# Output format is tab delimited.");
	# Reporting the fastq option.

	if globs['mapped']:
		printWrite(globs['logfilename'], globs['log-v'], "# --mapped : Only calculating scores for positions with reads mapped to them.");
	else:
		printWrite(globs['logfilename'], globs['log-v'], "# Calculating scores for every reference position specified.");
	# Reporting the mapped option.

	if globs['correct-opt']:
		printWrite(globs['logfilename'], globs['log-v'], "# --correct : Suggesting higher scoring alternative base when reference score is negative or reference base is N.");
	# Reporting the correct option.

	if globs['allcalc']:
		printWrite(globs['logfilename'], globs['log-v'], "# --allcalcs : Using tab delimited output and reporting extra columns.");
	# Reporting the allcalc option.

#############################################################################

def endProg(globs):
# A nice way to end the program.
	endtime = timeit.default_timer();
	totaltime = endtime - globs['starttime'];
	printWrite(globs['logfilename'], globs['log-v'], "#\n# Done!");
	printWrite(globs['logfilename'], globs['log-v'], "# The date and time at the end is: " + getDateTime());
	printWrite(globs['logfilename'], globs['log-v'], "# Total execution time: " + str(round(totaltime,3)) + " seconds.");
	printWrite(globs['logfilename'], globs['log-v'], "# =================================================");
	print("#");
	sys.exit();

#############################################################################

def getLogTime():
# Function to get the date and time in a certain format.
	return datetime.datetime.now().strftime("%I.%M.%S");

#############################################################################

def getDateTime():
# Function to get the date and time in a certain format.
	return datetime.datetime.now().strftime("%m.%d.%Y | %I:%M:%S");

#############################################################################

def getOutTime():
# Function to get the date and time in a certain format.
	return datetime.datetime.now().strftime("%m-%d-%Y.%I-%M-%S");

#############################################################################

def printWrite(o_name, v, o_line1, o_line2="", pad=0):
# Function to print a string AND write it to the file.
	if o_line2 == "":
		outline = o_line1;
	else:
		outline = o_line1 + " "*(pad-len(o_line1)) + o_line2;
	if v in [1,2]:
		print(outline);
	f = open(o_name, "a");
	f.write(outline + "\n");
	f.close();
	
#############################################################################

def report_stats(globs, msg="", step_start=0, stat_start=False, stat_end=False):
# Uses psutil to gather memory and time info between steps and print them to the screen.
	import timeit, psutil
	cur_time = timeit.default_timer();
	if stat_start:
	# The first time through just print the headers.
		globs['progstarttime'] = cur_time;
		printWrite(globs['logfilename'], globs['log-v'], "# --stats : Reporting Referee time and memory usage.");
		printWrite(globs['logfilename'], globs['log-v'], "\n# " + "-" * 120);
		printWrite(globs['logfilename'], globs['log-v'], "# Step" + " " * 15 + "Time since prev (sec)" + " " * 6 + "Elapsed time (sec)" + " " * 4 + "Current mem usage (MB)" + " " * 4 + "Virtual mem usage (MB)");
		printWrite(globs['logfilename'], globs['log-v'], "# " + "-" * 120);
	else:
		prog_elapsed = cur_time - globs['progstarttime'];
		step_elapsed = cur_time - step_start;
		mem = sum([p.memory_info()[0] for p in globs['pids']]) / float(2 ** 20);
		vmem = sum([p.memory_info()[1] for p in globs['pids']]) / float(2 ** 20);
		printWrite(globs['logfilename'], globs['log-v'], "# " + msg + " " * (19-len(msg)) + str(step_elapsed) + " " * (27-len(str(step_elapsed))) + str(prog_elapsed) + " " * (22-len(str(prog_elapsed))) + str(mem) + " " * (26-len(str(mem))) + str(vmem));
		if stat_end:
			printWrite(globs['logfilename'], globs['log-v'], "# " + "-" * 120);
	return cur_time;

#############################################################################

def getSubPID(n):
# Gets the process ids for the --stats option.
	import psutil
	return psutil.Process(os.getpid());

#############################################################################

def getFileLen(i_name):
# Gets the numebr of lines in a file.
	num_lines = 0;
	for line in getFileReader(i_name)(i_name).readlines(): num_lines += 1;
	return float(num_lines);

#############################################################################

def getFileReader(i_name):
# Check if a file is gzipped, and if so set gzip as the file reader. Otherwise, read as a normal text file.
	try:
		gzip_check = gzip.open(i_name).read(1);
		reader = gzip.open;
	except:
		reader = open;
	return reader;

#############################################################################

def getRandStr(strlen=6):
# This function generates a random string to add onto the end of tmp files to avoid possible overwrites.
	return ''.join(random.choice(string.ascii_letters) for m in xrange(strlen));
	
#############################################################################

def fastaReadInd(i_name):
# fastaGetFileInd reads a FASTA file and returns a dictionary containing file indexes for each title
# and sequence with the key:value format as [title start index]:[sequence start index]

	try:
		gzip_check = gzip.open(i_name).read(1);
		reader = gzip.open;
	except:
		reader = open;
	# Check if the genotype likelihood file is gzipped, and if so set gzip as the file reader. Otherwise, read as a normal text file.
	# MAKE SURE THIS WORKS WITH GZIPPED FILES!!

	with reader(i_name, "rb") as infile:
		fasta, first, curlist = {}, False, [];
		line = "derp";
		while line != '':
			line = infile.readline();
			if line[:1] == '>':
				if first:
					curseqend = infile.tell() - len(line) - 1;
					curlist.append(curseqend);
					fasta[cur_title] = curlist;
					curlist = [];

				cur_title = line[1:].strip().split(" ")[0];
				curtitlestart = infile.tell() - len(line);
				curtitleend = infile.tell() - 1;
				curseqstart = infile.tell();

				curlist.append(curtitlestart);
				curlist.append(curtitleend);
				curlist.append(curseqstart);

				first = True;

		curseqend = infile.tell() - len(line);
		curlist.append(curseqend);
		fasta[cur_title] = curlist;

	return fasta;
		
#############################################################################

def fastaGet(i_name, inds):
# This takes the file index for a corresponding FASTA title and sequence (as retrieved by
# fastaGetFileInd and returns the actual text of the title and the sequence.

	titlestart, titleend, seqstart, seqend = inds;

	with open(i_name, "rb") as infile:
		infile.seek(titlestart);
		title = infile.read(titleend - titlestart);

		infile.seek(seqstart);
		seq = infile.read(seqend - seqstart);

	title = title.replace("\n", "");
	seq = seq.replace("\n", "");

	return title, seq;

#############################################################################

def fastaRead(i_name, globs):
	# This function reads a FASTA file into a dictionary.
	try:
		gzip_check = gzip.open(i_name).read(1);
		reader = gzip.open;
	except:
		reader = open;
	# Check if the reference file is gzipped, and if so set gzip as the file reader. Otherwise, read as a normal text file.

	seqdict = {};
	for line in reader(i_name):
		line = line.strip();
		if line[0] == '>':
			curkey = line[1:];
			seqdict[curkey] = "";
		else:
			seqdict[curkey] = seqdict[curkey] + line;

	if len(seqdict) == 0:
		errorOut(10, "Failed to read reference genome as FASTA file.", globs);
	else:
		return seqdict;

#############################################################################

def welcome():
# Reads the ASCII art "Referee" text to be printed to the command line.
	return open("lib/ref-welcome.txt", "r").read();

#############################################################################














































































































































































































































































































































































































































































































































































































































































































































































def simpson():
	s = """
		              @                                                           
	             CC   CQ                                                      
	            /CCB @CC                                                      
	        GCCS CCCCCCC7                                                     
	         @CCCCCCCC@@@                                                     
	        @@@CCCCCCCCCCCCC                                                  
	        @CCCCCCCCCCCCCCCCC/                                               
	          OCCCCCCCCCCCCCCCCC                                              
	          @CCCCCCCCCCCCCCCCCCC@                                           
	          CCCCCCCCCCC@QCCCCCC@CCC(                                        
	          6CCCCCCCCCCCOCCCCCCCCC@es@                                      
	          @CCCCCCCCCCCCCCCCCCCCCCCCCC                                     
	          ^CCCCCCCCCCCCC@      @K      R                                  
	           CCCC@CCCCCCC                                                   
	          ~CCCC@CCCCCC@          G     //                   SCC@  @CC~    
	          @CCCCsCCCCCC#    S@    #       RS@                CCCB 6CCC     
	          @CCCCCCCCCOOG        S/@OC@CCSR  @/K             GCCCC@CCCC @CC 
	           @CC@GCCCCCCCCS      K67@CCCCCCCCG @             CCCCKCCCC@CCCC 
	          sCCCCCCCCCCCCCCCCCC77777SCCCCCCCCCCC        @@   CCCCKCCCCCCCCK 
	          CCCGRCCCCCCCCCCCCCCC777@CC@CCCCCCCCC       @CCCC@CCCCCCCCCCCCR  
	          @CCCK@CCCCCCCCCCCCCCCSQ(((((((((((@         6CCCCCCCCCCCCCCCC(  
	           ^QCCCCCCCCCCCCCCCC%(((((((((((((((((%@s     @CCCCCCCCCCCCCCC   
	            3CBCCCCCCCCCCR(((((((((((((((((((((((((%    CCCCCCC@CCCCCCC   
	           /CCCCCCCCCCC(((((((((((((((((((@((((@((@     SCCCCCCCCCCCCCC   
	           6CCCC@@CCCC(((((@   #@@@@       @@K          @KCCCCCC@CCCCCC   
	           CCCCCBCCCCC(((((@@@@@@@@(((3                @((#CCCCCKCCCCC    
	           CCCCSCCCCCC@((((@KK@KR@(((               %~(%(((%sCCCCCCCC     
	           ~@CCCCCCC@CCC((((((O@@@%((C             @~(((@(((((~(6((%      
	          (((((@CCCCRCCC@(((((((((((@@            @(((((((@t(((((((       
	          ((((((((@@@@CCC#(((((((((@%@(@         s(((((((((((((Ct(        
	         %(@(((((((((((((((((((@   /((((       @(((((((((((((((((@        
	        sR(((@((((((((((((((((@      (#%@G((((((((((((((((((((((@         
	      7~((((((((t@((((((((((G(s      ((((((((((((((((((((((((((R          
	     B((((((((((((((s#((((((((((/  s(e((((((((((((((((((((((((R           
	    @((((((((((((((((((((((((((((@((((@((((((((((((((((((((((/            
	   /(((((((((((((((((((((((((((((((((((((((((((((((((((((((C              
	   ~(((((((((((((((((((((((((((((e((((((((((((((((((((((((@               
	  @((((((((((((((((((((((((((((((@(((@(#((((((((((((((((K                 
	  G((((((((((((((((((((((((((((((s((((%@(((((((((((((((6                  
	  (((((((((((((((((((((((((((((((((((((e(((((((((((Q/                     
	 G((((((((((((((@((((((((((((((((((((((%(((((((@                          
	 @(((((((((((((C(((((((((((((((((((t(((G(                                 
	 ~(((((((((((((((((((((((((((((((((t(((e(s                                
	@(((((((((((((((((((((((((((((((((((((((((                                
	7(((((((((((((6((((((((((((((((((((Q((((((%   
	"""

	print(s);
