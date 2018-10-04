#!/usr/bin/python
#############################################################################
# Reference genome quality score annotation
# This is the main interface.
#
# Gres Thomagg
# Fall 2018
#############################################################################

import sys, os, multiprocessing as mp, shutil, lib.refcore as RC, lib.ref_calc as CALC, \
	lib.opt_parse as OP, lib.ref_out as OUT, lib.global_vars as GV

#############################################################################

def referee(globs):
	files, globs, step_start_time = OP.optParse(globs);
	# Getting the input parameters from optParse.

	if globs['stats']:
		step_start_time  = RC.report_stats(globs, "Index ref fasta", step_start=step_start_time);
	globs['ref'] = RC.fastaReadInd(globs['reffile']);
	# Index the reference FASTA file.

	print files;

	for file_num in files:
	# Do calculations for each file in the files dictionary. If input mode is -gl this is just a single 
	# file. If input mode is -i this should be multiple files.
		if globs['stats']:
			step_start_time  = RC.report_stats(globs, "Calcs " + str(file_num), step_start=step_start_time);
		# Step update for --stats.

		with open(files[file_num]['in'], "r") as infile, open(files[file_num]['out'], "w") as outfile:
			if globs['num-procs'] == 1:
				for line in infile:
					outdict = CALC.refCalc((line, globs));
					OUT.outputTab(outdict, outfile, globs);
			# A serial version.
			else:
				pool = mp.Pool(processes = globs['num-procs']);

				if globs['stats']:
					for result in pool.map(RC.getSubPID, range(globs['num-procs'])):
						globs['pids'].append(result);
				for outdict in pool.map(CALC.refCalc, ((line, globs) for line in infile)):
					OUT.outputTab(outdict, outfile,  globs);
			# The parallel version.
		# Do the calculations on each input file.

	if not globs['mapped']:
		for file_num in files:
			if globs['stats']:
				step_start_time  = RC.report_stats(globs, "Add unmapped " + str(file_num), step_start=step_start_time);
			OUT.addUnmapped(files[file_num], globs);
			RC.printWrite(globs['logfilename'], globs['log-v'], "+ Renaming tmp file to output file: " + files[file_num]['tmpfile'] + " -> " + files[file_num]['out']);
			shutil.move(files[file_num]['tmpfile'], files[file_num]['out']);
	# If all positions are to be assigned a score, this fills in the unmapped positions. Requires one pass through of the output file.

	if globs['stats']:
		step_start_time = RC.report_stats(globs, "End program", step_start=step_start_time, stat_end=True);
	# A step update for --stats.

	return;
#############################################################################

if __name__ == '__main__':
# Main is necessary for multiprocessing to work on Windows.
	globs = GV.init();
	RC.startProg(globs);
	referee(globs);
	RC.endProg(globs);

#############################################################################