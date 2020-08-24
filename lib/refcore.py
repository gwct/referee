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
	printWrite(globs['logfilename'], globs['log-v'], "\n" + border + "\n" + fullmsg + "\n" + border + "\n");
	if globs['endprog']:
		globs['exit-code'] = 1;
		endProg(globs);
	else:
		printWrite(globs['logfilename'], globs['log-v'], "\nScript call: " + " ".join(sys.argv));
		sys.exit(1);

#############################################################################

def endProg(globs):
# A nice way to end the program.
	endtime = timeit.default_timer();
	totaltime = endtime - globs['starttime'];
	printWrite(globs['logfilename'], globs['log-v'], "#\n# Done!");
	printWrite(globs['logfilename'], globs['log-v'], "# The date and time at the end is: " + getDateTime());
	printWrite(globs['logfilename'], globs['log-v'], "# Total execution time:            " + str(round(totaltime,3)) + " seconds.");
	printWrite(globs['logfilename'], globs['log-v'], "# Output directory for this run:   " + globs['out-dir']);
	printWrite(globs['logfilename'], globs['log-v'], "# Log file for this run:           " + globs['logfilename']);
	printWrite(globs['logfilename'], globs['log-v'], "# =================================================");
	print("#");
	sys.exit(globs['exit-code']);

#############################################################################

def getDate():
# Function to get the date and time in a certain format.
	return datetime.datetime.now().strftime("%m.%d.%Y");

#############################################################################

def getTime():
# Function to get the date and time in a certain format.
	return datetime.datetime.now().strftime("%H:%M:%S");

#############################################################################

def getDateTime():
# Function to get the date and time in a certain format.
	return datetime.datetime.now().strftime("%m.%d.%Y | %I:%M:%S");

#############################################################################

def getOutTime():
# Function to get the date and time in a certain format.
	return datetime.datetime.now().strftime("%m-%d-%Y.%I-%M-%S");

#############################################################################

def printWrite(o_name, v, outline):
# Function to print a string AND write it to the file.
	if v in [-1,1,2]:
		print(outline);
	if v != -1:
		f = open(o_name, "a");
		f.write(outline + "\n");
		f.close();

#############################################################################
	
def spacedOut(string, totlen):
#Properly adds spaces to the end of a message to make it a given length
	spaces = " " * (totlen - len(string));
	return string + spaces;

#############################################################################

def report_step(globs, step, step_start_time, step_status, start=False):
# Uses psutil to gather memory and time info between steps and print them to the screen.
	#log = logger(globs['logfilename']);

	dashes = 150
	if globs['psutil']:
		import psutil;
		dashes = 175;

	cur_time = timeit.default_timer();
	col_widths = [ 14, 10, 40, 30, 20, 16 ];
	if globs['psutil']:
		col_widths += [25, 20];
	if start:
		headers = [ "# Date", "Time", "Current step", "Status", "Elapsed time (s)", "Step time (s)" ];
		if globs['psutil']:
			headers += ["Current mem usage (MB)", "Virtual mem usage (MB)"]

		headers = "".join([ spacedOut(str(headers[i]), col_widths[i]) for i in range(len(headers)) ]);

		printWrite(globs['logfilename'], globs['log-v'], "# " + "-" * dashes);
		printWrite(globs['logfilename'], globs['log-v'], headers);
		printWrite(globs['logfilename'], globs['log-v'], "# " + "-" * dashes);

	else:
		prog_elapsed = str(round(cur_time - globs['starttime'], 5));
		if not step_start_time:
			out_line = [ "# " + getDate(), getTime(), step, step_status ];
			term_col_widths = col_widths[:4];
			out_line = [ spacedOut(str(out_line[i]), term_col_widths[i]) for i in range(len(out_line)) ];
			sys.stdout.write("".join(out_line));
			sys.stdout.flush();


		else:
			step_elapsed = str(round(cur_time - step_start_time, 5));
			out_line = [ step_status, prog_elapsed, step_elapsed ];
			if globs['psutil']:
				mem = round(sum([p.memory_info()[0] for p in globs['pids']]) / float(2 ** 20), 5);
				vmem = round(sum([p.memory_info()[1] for p in globs['pids']]) / float(2 ** 20), 5);
				out_line += [str(mem), str(vmem)];
			term_col_widths = col_widths[3:];
			file_line = [ "# " + getDate(), getTime(), step ] + out_line;
			file_col_widths = col_widths[:3] + [30] + col_widths[4:];
			
			out_line = [ spacedOut(str(out_line[i]), term_col_widths[i]) for i in range(len(out_line)) ];
			sys.stdout.write("\b" * 30);
			sys.stdout.write("".join(out_line) + "\n");
			sys.stdout.flush();
			#print(file_col_widths);
			file_line = [ spacedOut(str(file_line[i]), file_col_widths[i]) for i in range(len(file_line)) ];
			printWrite(globs['logfilename'], 3, "".join(file_line));
	return cur_time;

#############################################################################

def getFileReader(i_name):
# Check if a file is gzipped, and if so set gzip as the file reader. Otherwise, read as a normal text file.
	try:
		gzip_check = gzip.open(i_name, "r").read(1);
		# print("HI")
		# print(gzip_check.decode());
		reader = gzip.open;
		#sys.exit();
	except:
		reader = open;
	return reader;

#############################################################################
# The two line reader functions based on whether the input file is gzipped or not
def readLine(line):
	return line.strip().split("\t");

def readGzipLine(line):
	return line.decode().strip().split("\t");

#############################################################################

def mapQCheck(infile):
	with open(infile) as f:
		first_line = f.readline().split("\t");
	if len(first_line) != 7:
		return False;
	else:
		return True;

#############################################################################

def fastaReadInd(i_name, globs):
# fastaGetFileInd reads a FASTA file and returns a dictionary containing file indexes for each title
# and sequence with the key:value format as [title start index]:[sequence start index]

	reader = getFileReader(i_name);
	if reader != open:
		errorOut("CORE1", "FASTA indexing requires the reference FASTA (-ref) to be uncompressed. Please gunzip the file and try again.", globs)

	# if reader == open:
	# 	freadline = lambda f : f.readline();
	# else:
	#	freadline = lambda f : f.readline().decode();

	# try:
	# 	gzip_check = gzip.open(i_name).read(1);
	# 	reader = gzip.open;
    #     #lread = lambda l : l.decode().rstrip();                
	# except:
	# 	reader = open;
		#lread = lambda l : l.rstrip();
	# Check if the fasta file is gzipped, and if so set gzip as the file reader. Otherwise, read as a normal text file.
	# Can't get the FASTA indexing to work on .gz files... just going to throw an error if -ref is .gz for now.

	with reader(i_name, "r") as infile:
		fasta, first, curlist = {}, False, [];
		line = "blah";
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

	with open(i_name, "r") as infile:
		infile.seek(titlestart);
		title = infile.read(titleend - titlestart);

		infile.seek(seqstart);
		seq = infile.read(seqend - seqstart);

	title = title.replace("\n", "");
	seq = seq.replace("\n", "");

	return title, seq;

#############################################################################

def getScaffLens(scaff, globs):
# Gets the lengths of each scaffold in the input file after indexing
	seq = fastaGet(globs['ref-file'], globs['ref'][scaff])[1];
	return len(seq);

#############################################################################

def chunks(l, n):
# Splits a list l into even chunks of size n.
    n = max(1, n);
    return (l[i:i+n] for i in range(0, len(l), n));

#############################################################################

def isPosInt(numstr):
# Check if a string is a positive integer
	try:
		num = int(numstr);
	except:
		return False;

	if num > 0:
		return num;
	else:
		return False;
#############################################################################

def welcome():
# Reads the ASCII art "Referee" text to be printed to the command line.
	return open(os.path.join(os.path.dirname(__file__), "ref-welcome.txt"), "r").read();

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
