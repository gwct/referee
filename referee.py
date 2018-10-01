#!/usr/bin/python
#############################################################################
# Reference genome quality score annotation
# This is the main interface.
#
# Gregg Thomas
# Fall 2018
#############################################################################

import sys, os, multiprocessing as mp, lib.refcore as RC, lib.ref_calc as CALC, \
	lib.opt_parse as OP, lib.global_vars as GV
try:
	from Bio import SeqIO
except:
	sys.exit("\n*** ERROR: Your installation of Python is missing the Biopython module. Please install the module.\n");
# Have to have Biopython to read the FASTA files.

#############################################################################

def referee(globs):
	files = OP.optParse(globs);
	# Getting the input parameters from optParse.

	if globs['stats']:
		import psutil
		pids = [psutil.Process(os.getpid())];		
		prog_start_time = RC.report_stats(globs, stat_start=True);
		step_start_time = prog_start_time;
		# Initializing if --stats is set.

		step_start_time = RC.report_stats(globs, "Caclulate scores", pids, step_start_time, prog_start_time);
		# The first step.

	if globs['num-procs'] == 1:
		for f in files.iteritems():
			CALC.refCalc(f);
	# A serial version.
	else:
		if len(files) != 1:
			files = OP.multiPrep(files);
		print files;
		pool = mp.Pool(processes = globs['num-procs']);
		for result in pool.imap_unordered(CALC.refCalc, files.iteritems()):
			continue;
	# The parallel version

	if globs['stats']:
		step_start_time = RC.report_stats(globs, "End program", pids, step_start_time, prog_start_time, stat_end=True);

	return;
#############################################################################

if __name__ == '__main__':
# Main is necessary for multiprocessing to work on Windows.
	globs =  GV.init();
	print("#");
	RC.printWrite(globs['logfilename'], globs['log-v'], "# =========================================================================");
	RC.printWrite(globs['logfilename'], globs['log-v'], "# Welcome to Referee -- Reference genome quality score calculator.");
	RC.printWrite(globs['logfilename'], globs['log-v'], "# The date and time at the start is: " + RC.getDateTime());
	RC.printWrite(globs['logfilename'], globs['log-v'], "# The program was called as: " + " ".join(sys.argv));
	RC.printWrite(globs['logfilename'], globs['log-v'], "#\n# " + "-" * 40 + "\n#");
	RC.printWrite(globs['logfilename'], globs['log-v'], "# ** IMPORTANT!");
	RC.printWrite(globs['logfilename'], globs['log-v'], "# ** Input columns: Scaffold\tPosition\tAA\tAC\tAG\tAT\tCC\tCG\tCT\tGG\tGT\tTT");
	RC.printWrite(globs['logfilename'], globs['log-v'], "# ** Please ensure that your input genotype likelihood files are tab delimited with columns in this exact order.");
	RC.printWrite(globs['logfilename'], globs['log-v'], "# ** Failure to do so will result in inaccurate calculations!!");
	RC.printWrite(globs['logfilename'], globs['log-v'], "#\n# " + "-" * 40 + "\n#");
	referee(globs);
	RC.endProg(globs);

#############################################################################