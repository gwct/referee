#!/usr/bin/python
#############################################################################
# Reference genome quality score annotation
# This is the main interface.
#
# Gres Thomagg
# Fall 2018
#############################################################################

import sys, os, multiprocessing as mp, lib.refcore as RC, lib.ref_calc as CALC, \
	lib.opt_parse as OP, lib.ref_out as OUT, lib.global_vars as GV
try:
	from Bio import SeqIO
except:
	sys.exit("\n*** ERROR: Your installation of Python is missing the Biopython module. Please install the module.\n");
# Have to have Biopython to read the FASTA files.

#############################################################################

def referee(globs):
	files, globs, step_start_time = OP.optParse(globs);
	# Getting the input parameters from optParse.

	if globs['stats']:
		step_start_time  = RC.report_stats(globs, "Index ref fasta", step_start=step_start_time);
	globs['ref'] = RC.fastaReadInd(globs['reffile']);
	# Index the reference FASTA file.

	for file_num in files:
		if globs['stats']:
			step_start_time  = RC.report_stats(globs, "Calcs " + str(file_num), step_start=step_start_time);

		with open(files[file_num]['in'], "r") as infile, open(files[file_num]['out'], "w") as outfile:
			if globs['num-procs'] == 1:
				for line in infile:
					outdict = CALC.refCalc2((line, globs));
					OUT.outputTab(outdict, outfile, globs);
			# A serial version.
			else:
				pool = mp.Pool(processes = globs['num-procs']);

				if globs['stats']:
					for result in pool.map(RC.getSubPID, range(globs['num-procs'])):
						globs['pids'].append(result);
				for outdict in pool.map(CALC.refCalc2, ((line, globs) for line in infile)):
					OUT.outputTab(outdict, outfile,  globs);
			# The parallel version.
		# Do the calculations on each input file.

	if not globs['mapped']:
		for file_num in files:
			if globs['stats']:
				step_start_time  = RC.report_stats(globs, "Add unmapped " + str(file_num), step_start=step_start_time);
			OUT.addUnmapped(files[file_num], globs);
			RC.printWrite(globs['logfilename'], globs['log-v'], "+ Renaming tmp file to output file: " + files[file_num]['tmpfile'] + " -> " + files[file_num]['out']);
			os.rename(files[file_num]['tmpfile'], files[file_num]['out']);



		# if globs['fastq']:
		# 	fq_seq, fq_scores, fq_curlen, fq_lastpos = [], [], 0, 1;
		# if globs['fastq']:
		# 	fq_seq, fq_scores, fq_curlen, fq_lastpos = OUT.outputFastq(outdict, outfile, fq_seq, fq_scores, fq_curlen, fq_lastpos, globs);
		# else:

	# if globs['num-procs'] == 1:
	# 	if globs['stats']:
	# 		globs['stepstartime'] = RC.report_stats(globs, "Calculating scores");
	# 	for f in files.iteritems():
	# 		CALC.refCalc(f);
	# # A serial version.
	# else:
	# 	if len(files) == 1:
	# 		if globs['stats']:
	# 			globs['stepstartime'] = RC.report_stats(globs, "Splitting files");
	# 		files = OP.multiPrep(files);
	# 	pool = mp.Pool(processes = globs['num-procs']);

	# 	if globs['stats']:
	# 		globs['stepstartime'] = RC.report_stats(globs, "Calculating scores");
	# 		for result in pool.imap_unordered(RC.getSubPID, range(globs['num-procs'])):
	# 			globs['pids'].append(result);

	# 	for result in pool.imap_unordered(CALC.refCalc, files.iteritems()):
	# 		continue;
	# # The parallel version

	if globs['stats']:
		step_start_time = RC.report_stats(globs, "End program", step_start=step_start_time, stat_end=True);

	return;
#############################################################################

if __name__ == '__main__':
# Main is necessary for multiprocessing to work on Windows.
	globs = GV.init();
	RC.startProg(globs);
	referee(globs);
	RC.endProg(globs);

#############################################################################