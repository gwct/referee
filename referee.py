#!/usr/bin/python
#############################################################################
# Reference genome quality score annotation
# This is the main interface.
#
# Gregg Thomas
# Fall 2018
# Summer 2020 update: fixed multiprocessing to read chunks of input at a time
# rather than split files.
#############################################################################

import sys, os, multiprocessing as mp, shutil, gzip, lib.refcore as RC, lib.ref_calc as CALC, \
	lib.opt_parse as OP, lib.ref_out as OUT, lib.global_vars as GV

#############################################################################

def referee(globs):
	step_start_time = RC.report_step(globs, "", "", "", start=True);
	# Initialize the step headers

	step = "Detecting compression"
	step_start_time = RC.report_step(globs, step, False, "In progress...");
	globs['reader'] = RC.getFileReader(globs['in-file']);
	if globs['reader'] != open:
		globs['lread'] = RC.readGzipLine
		globs['read-mode'] = "rb";
	step_start_time = RC.report_step(globs, step, step_start_time, "Success!");
	#print("\n", globs['reader'], globs['lread'], globs['read-mode']);
	# Detect whether the input file is gzip compressed or not and save the appropriate functions.

	step = "Indexing reference FASTA"
	step_start_time = RC.report_step(globs, step, False, "In progress...");
	globs['ref'] = RC.fastaReadInd(globs['ref-file'], globs);
	step_start_time = RC.report_step(globs, step, step_start_time, "Success!");
	# Index the reference FASTA file.

	if globs['ref-index']:
		step = "Getting scaffold lengths from index"
		step_start_time = RC.report_step(globs, step, False, "In progress...");
		for line in open(globs['ref-index']):
			line = line.split("\t");
			globs['scaff-lens'][line[0]] = int(line[1]);
	else:
		RC.printWrite(globs['logfilename'], globs['log-v'], "# WARNING 1: Cannot find reference index file (" + globs['ref-file'] + ".fai)");
		RC.printWrite(globs['logfilename'], globs['log-v'], "# WARNING 1: Will read reference scaffold lengths manually, which can take a few minutes.");		
		step = "Getting scaffold lengths manually"
		step_start_time = RC.report_step(globs, step, False, "In progress...");
		for scaff in globs['ref']:
			seq = RC.fastaGet(globs['ref-file'], globs['ref'][scaff])[1];
			globs['scaff-lens'][scaff] = len(seq);
	step_start_time = RC.report_step(globs, step, step_start_time, "Success! Read " + str(len(globs['scaff-lens'])) + " scaffolds");
	# Getting scaffold lengths

	if globs['pileup-opt']:
		step = "Computing likelihood look-up table"
		step_start_time = RC.report_step(globs, step, False, "In progress...");
		globs['probs'] = CALC.glInit(globs['mapq-opt'], globs['haploid-opt']);
		step_start_time = RC.report_step(globs, step, step_start_time, "Success!");
	# Pre-compute the likelihoods for every base-quality (+ mapping quality if set) so they can
	# just be looked up for each position.

	with open(globs['out-tab'], "w") as outfile, mp.Pool(processes=globs['num-procs']) as pool:
		if globs['fastq-opt']:
			fastqfile = open(globs['out-fq'], "w");
		else:
			fastqfile = "";
		# Open the FASTQ file if --fastq is specified. Otherwise just set an empty string instead of the stream.

		if globs['bed-opt']:
			for line in globs['reader'](globs['in-file'], globs['read-mode']):
				first_scaff = globs['lread'](line)[0];
				break;
			globs['cur-bed'] = OUT.initializeBed(first_scaff, globs);
		# Initialize first scaffold for BED output.

		cur_lines, outdicts = [], [];
		i, i_start = 0, 1;
		prev_scaff, prev_pos = "", 1;
		for line in globs['reader'](globs['in-file'], globs['read-mode']):
			i += 1;
			cur_lines.append(line);
			if len(cur_lines) == globs['chunk-size']:
				step = "Processing lines " + str(i_start) + "-" + str(i);
				step_start_time = RC.report_step(globs, step, False, "In progress...");

				i_start = i + 1;
				line_chunks = list(RC.chunks(cur_lines, globs['lines-per-proc']));
				for result in pool.starmap(CALC.refCalc, ((line_chunk, globs) for line_chunk in line_chunks)):
					outdicts += result;
					#for site in result:
						#print(site);
						#print(result[site]);
						#prev_scaff, prev_pos = OUT.outputDistributor(result[site], prev_scaff, prev_pos, outfile, fastqfile, globs);
				for outdict in outdicts:
					prev_scaff, prev_pos = OUT.outputDistributor(outdict, prev_scaff, prev_pos, outfile, fastqfile, globs);
				cur_lines, outdicts = [], [];
				step_start_time = RC.report_step(globs, step, step_start_time, "Success!");
		# Read the input file line by line. Once a certain number of lines have been read, pass them to siteParse in parallel.

		if cur_lines != []:
			step = "Processing lines "  + str(i_start) + "-" + str(i);
			step_start_time = RC.report_step(globs, step, False, "In progress...");

			line_chunks = list(RC.chunks(cur_lines, globs['lines-per-proc']));
			for result in pool.starmap(CALC.refCalc, ((line_chunk, globs) for line_chunk in line_chunks)):
				outdicts += result;
				# for site in result:
					#print(site);
					#print(result[site]);
					#prev_scaff, prev_pos = OUT.outputDistributor(result[site], prev_scaff, prev_pos, outfile, fastqfile, globs);
			for outdict in outdicts:
				prev_scaff, prev_pos = OUT.outputDistributor(outdict, prev_scaff, prev_pos, outfile, fastqfile, globs);	
			step_start_time = RC.report_step(globs, step, step_start_time, "Success!");
		# Read the input file line by line. Once a certain number of lines hav
		# Count the last chunk of lines if necessary.

		if prev_pos != globs['scaff-lens'][prev_scaff]:
			step = "Filling final unmapped positions"
			step_start_time = RC.report_step(globs, step, False, "In progress...");
			seq = RC.fastaGet(globs['ref-file'], globs['ref'][prev_scaff])[1];
			outdict = { 'scaff' : prev_scaff, 'pos' : globs['scaff-lens'][prev_scaff], 'ref' : seq[prev_pos-1], 
                        'rq' : -2, 'raw' : "NA", 'lr' : "NA", 'l_match' : "NA", 
                        'l_mismatch' : "NA", 'gls' : "NA", 'cor_ref' : "NA", 
                        'cor_score' : "NA", 'cor_raw' : "NA" };
			prev_scaff, prev_pos = OUT.outputDistributor(outdict, prev_scaff, prev_pos, outfile, fastqfile, globs)
			step_start_time = RC.report_step(globs, step, step_start_time, "Success!");
		# If the last positions are unmapped they won't have been filled in. Do that here using the last position (length) of the
		# previous scaffold as the outdict.

		if globs['fastq-opt']:
			fastqfile.close();
		# Close the FASTQ file if --fastq was set.

		if globs['bed-opt']:
			step = "Writing final bed file"
			step_start_time = RC.report_step(globs, step, False, "In progress...");
			OUT.outputBed(globs['cur-bed']);
			step_start_time = RC.report_step(globs, step, step_start_time, "Success!");
		# Write out the last bed file.

	return;
#############################################################################

if __name__ == '__main__':
# Main is necessary for multiprocessing to work on Windows.
	globs = GV.init();
	
	if any(v in sys.argv for v in ["--version", "-version", "--v", "-v"]):
		sys.exit("# Referee version " + globs['version'] + " released on " + globs['releasedate']);
	# The version option to simply print the version and exit.

	print("#");
	print("# =================================================");
	print(RC.welcome());
	print("    Reference genome quality score calculator.\n");
	if "-h" not in sys.argv:
		print("       Pseudo assembly by iterative mapping.\n");
	# A welcome banner.

	globs = OP.optParse(globs);
	# Getting the input parameters from optParse.

	if globs['norun']:
		sys.exit("# --norun SET. EXITING AFTER PRINTING OPTIONS INFO...\n#");

	referee(globs);
	RC.endProg(globs);

#############################################################################

