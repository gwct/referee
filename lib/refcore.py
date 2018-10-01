from __future__ import print_function
#############################################################################
# Referee CORE functions
# Gregg Thomas
# August 2013-present
# Forked from core on 12.13.2015
#############################################################################

import sys, os, timeit, subprocess, datetime, time, opt_parse as OP
from Bio import SeqIO

#############################################################################

def errorOut(errnum, errmsg, globs):
# Formatting for error messages.
	#OP.optParse(1);
	fullmsg = "|**Error " + str(errnum) + ": " + errmsg + " |";
	border = " " + "-" * (len(fullmsg)-2);
	fullstr = "\n" + border + "\n" + fullmsg + "\n" + border + "\n"
	printWrite(globs['logfilename'], globs['log-v'], "\n" + border + "\n" + fullmsg + "\n" + border + "\n")
	endProg(globs);

#############################################################################

def endProg(globs):
# A nice way to end the program.
	endtime = timeit.default_timer();
	totaltime = endtime - globs['starttime'];
	printWrite(globs['logfilename'], globs['log-v'], "#\n# The date and time at the end is: " + getDateTime());
	printWrite(globs['logfilename'], globs['log-v'], "# Total execution time: " + str(round(totaltime,3)) + " seconds.");
	printWrite(globs['logfilename'], globs['log-v'], "# =========================================================================\n#");
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

def filePrep(filename, header=""):
# Function to initialize output files with headers or as blank files.
	if header != "" and header[-1] != "\n":
		header += "\n";
	outfile = open(filename, "w");
	outfile.write(header);
	outfile.close();

#############################################################################

def printWrite(o_name, v, o_line1, o_line2="", pad=0):
#Function to print a string AND write it to the file.
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

# def printStep(step, msg):
# # Prints a message and increments a counter.
# 	if globs.v not in [-2,-1]:
# 		print(msg);
# 	return step+1;

#############################################################################

def report_stats(globs, msg="", procs="", step_start=0, prog_start=0, stat_start=False, stat_end=False):
	import timeit, psutil
	#func_v = -2 if globs.v == -2 else 1;
	# func_v = 1;
	cur_time = timeit.default_timer();
	#logfilename = os.path.join(outdir, "grampa_stats.log");
	if stat_start:
		printWrite(globs['logfilename'], globs['log-v'], "# --stats : Reporting Referee time and memory usage.");
		printWrite(globs['logfilename'], globs['log-v'], "# " + "-" * 120);
		printWrite(globs['logfilename'], globs['log-v'], "# Step" + " " * 15 + "Step time (sec)" + " " * 6 + "Elapsed time (sec)" + " " * 4 + "Current mem usage (MB)" + " " * 4 + "Virtual mem usage (MB)");
		printWrite(globs['logfilename'], globs['log-v'], "# " + "-" * 120);
	else:
		prog_elapsed = cur_time - prog_start;
		step_elapsed = cur_time - step_start;
		mem = sum([p.memory_info()[0] for p in procs]) / float(2 ** 20);
		vmem = sum([p.memory_info()[1] for p in procs]) / float(2 ** 20);
		printWrite(globs['logfilename'], globs['log-v'], "# " + msg + " " * (19-len(msg)) + str(step_elapsed) + " " * (21-len(str(step_elapsed))) + str(prog_elapsed) + " " * (22-len(str(prog_elapsed))) + str(mem) + " " * (26-len(str(mem))) + str(vmem));
		if stat_end:
			printWrite(globs['logfilename'], globs['log-v'], "# " + "-" * 120);

	return cur_time;

#############################################################################

def getSubPID(n):
	import psutil
	return psutil.Process(os.getpid());

#############################################################################

def osCheck(test_cmd):
# For the tests script. Need to know if we are on Windows in order to pass the command correctly.
	import platform
	if platform.system == 'Windows':
		test_cmd = " ".join(test_cmd);
	return test_cmd;

#############################################################################

def testPrep():
# Prepares the test command and calls the tests script.
	t_path = os.path.join(os.path.dirname(__file__), "tests.py");
	pyver = sys.version[:3];
	try:
		python_cmd = "python" + pyver
		test_cmd = [python_cmd, t_path, python_cmd];
		subprocess.call(osCheck(test_cmd));
	except OSError:
		python_cmd = "python"
		test_cmd = [python_cmd, t_path, python_cmd];
		subprocess.call(osCheck(test_cmd));

#############################################################################

def getFileLen(i_name):
	num_lines = 0;
	for line in open(i_name).xreadlines(): num_lines += 1;
	return float(num_lines);

#############################################################################

def getFastaInfo(ref_name, scaff_id):
	for record in SeqIO.parse(ref_name, "fasta"):
		if record.id == scaff_id:
			seq = record.seq;
			seqlen = len(record.seq);
			break;
	return seq, seqlen;

#############################################################################

def getScaffLens(ref_file):
	cur_lens = {};
	for record in SeqIO.parse(ref_name, "fasta"):
		cur_lens[record.id] = len(record.seq);
	return cur_lens;

#############################################################################

def getNumPos(i_name, ref_file, start_pos, end_pos, mapped):
	num_pos, last_scaff = 0,0;
	if not mapped and end_pos:
		num_pos = end_pos - start_pos;
	else:
		for line in open(i_name):
			line = line.strip().split("\t")[1];
			if not mapped:


			scaff, pos = line[0], int(line[1]);




			if not end_pos and scaff != last_scaff:
				seq, end_pos = getFastaInfo(ref_file, scaff);



			if pos < start_pos:
				continue;
		




	for line in open(i_name):
		pass;
	return float(line.split("\t")[1]); 





































































































































































































































































































































































































































































































































































































































































































































































































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
