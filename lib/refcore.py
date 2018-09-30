from __future__ import print_function
#############################################################################
# Referee CORE functions
# Gregg Thomas
# August 2013-present
# Forked from core on 12.13.2015
#############################################################################

import sys, os, timeit, subprocess, datetime, time, opt_parse as OP, global_vars as globs

#############################################################################

def errorOut(errnum, errmsg):
# Formatting for error messages.
	#OP.optParse(1);
	fullmsg = "|**Error " + str(errnum) + ": " + errmsg + " |";
	border = " " + "-" * (len(fullmsg)-2);
	fullstr = "\n" + border + "\n" + fullmsg + "\n" + border + "\n"
	printWrite(globs.logfilename, globs.log_v, "\n" + border + "\n" + fullmsg + "\n" + border + "\n")
	endProg();

#############################################################################

def endProg():
# A nice way to end the program.
	endtime = timeit.default_timer();
	totaltime = endtime - globs.starttime;
	printWrite(globs.logfilename, globs.log_v, "# The date and time at the end is: " + getDateTime());
	printWrite(globs.logfilename, globs.log_v, "# Total execution time: " + str(round(totaltime,3)) + " seconds.");
	printWrite(globs.logfilename, globs.log_v, "# =========================================================================\n");
	sys.exit();

#############################################################################

def getLogTime():
# Function to get the date and time in a certain format.
	return datetime.datetime.now().strftime("%I.%M.%S");
	# return datetime.datetime.now().strftime("%m.%d.%Y-%I.%M.%S");

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

def loadingBar(counter, length, done, bars):
#This function serves as a text loading bar for long scripts with counters. The following
#lines must be added within the script to initialize and terminate the script:
#Initilization:
#numlines = core.getFileLen(alnfilename);
#numbars = 0;
#donepercent = [];
#i = 0;
#Termination:
#	pstring = "100.0% complete.";
#	sys.stderr.write('\b' * len(pstring) + pstring);
#	print "\nDone!";
#
#If length is lines in a file use the core.getFileLen function to get the number of lines in the file

	percent = float(counter) / float(length) * 100.0;
	percentdone = int(percent);

	p = str(percent)
	pstring = " " + p[:5] + "% complete.";

	if percentdone % 2 == 0 and done != None and percentdone not in done:
		loading = "";
		loading = "[";
		j = 0;
		while j <= bars:
			loading = loading + "*";
			j = j + 1;
		while j < 50:
			loading = loading + "-";
			j = j + 1;
		loading = loading + "]";

		loading = loading + "                 ";
		sys.stderr.write('\b' * len(loading) + loading);

		done.append(percentdone);
		bars = bars + 1;

	sys.stderr.write('\b' * len(pstring) + pstring);

	return bars, done;

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

def printStep(step, msg):
# Prints a message and increments a counter.
	if globs.v not in [-2,-1]:
		print(msg);
	return step+1;

#############################################################################

def report_stats(msg="", procs="", step_start=0, prog_start=0, stat_start=False):
	import timeit, psutil
	#func_v = -2 if globs.v == -2 else 1;
	# func_v = 1;
	cur_time = timeit.default_timer();
	#logfilename = os.path.join(outdir, "grampa_stats.log");
	if stat_start:
		printWrite(globs.logfilename, globs.log_v, "# --stats : Reporting Referee time and memory usage.");
		printWrite(globs.logfilename, globs.log_v, "# " + "-" * 120);
		printWrite(globs.logfilename, globs.log_v, "# Step" + " " * 13 + "Step time (sec)" + " " * 6 + "Elapsed time (sec)" + " " * 4 + "Current mem usage (MB)" + " " * 4 + "Virtual mem usage (MB)");
		printWrite(globs.logfilename, globs.log_v, "# " + "-" * 120);
	else:
		prog_elapsed = cur_time - prog_start;
		step_elapsed = cur_time - step_start;
		mem = sum([p.memory_info()[0] for p in procs]) / float(2 ** 20);
		vmem = sum([p.memory_info()[1] for p in procs]) / float(2 ** 20);
		printWrite(globs.logfilename, globs.log_v, msg + " " * (19-len(msg)) + str(step_elapsed) + " " * (21-len(str(step_elapsed))) + str(prog_elapsed) + " " * (22-len(str(prog_elapsed))) + str(mem) + " " * (26-len(str(mem))) + str(vmem));
	return cur_time

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
