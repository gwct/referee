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
	globs['ref'], prev_scaff = RC.fastaReadInd(globs['ref-file'], globs);
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
	step_start_time = RC.report_step(globs, step, step_start_time, "Success!");
	globs['num-pos'], globs['num-scaff'] = sum(globs['scaff-lens'].values()), len(globs['scaff-lens'])
	RC.printWrite(globs['logfilename'], globs['log-v'], "# Read " + str(globs['num-pos']) + " positions in " + str(globs['num-scaff']) + " scaffolds");
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

		if globs['fasta-opt']:
			fastafile = open(globs['out-fa'], "w");
		else:
			fastafile = "";
		# Open the FASTA file if --fasta is specified. Otherwise just set an empty string instead of the stream.

		if globs['bed-opt']:
			for line in globs['reader'](globs['in-file'], globs['read-mode']):
				first_scaff = globs['lread'](line)[0];
				break;
			globs['cur-bed'] = OUT.initializeBed(first_scaff, globs);
		# Initialize first scaffold for BED output.

		cur_lines, outdicts = [], [];
		i, i_start, next_pos = 0, 1, 1;
		for line in globs['reader'](globs['in-file'], globs['read-mode']):
			i += 1;
			cur_lines.append(line);
			if len(cur_lines) == globs['chunk-size']:
				step = "Processing lines " + str(i_start) + "-" + str(i);
				step_start_time = RC.report_step(globs, step, False, "In progress...");

				i_start = i + 1;
				line_chunks = list(RC.chunks(cur_lines, globs['lines-per-proc']));
				for result in pool.starmap(CALC.refCalc, ((line_chunk, globs) for line_chunk in line_chunks)):
					#outdicts += result;
					for outdict in result:
						# print(site);
						# print(result[site]);
						prev_scaff, next_pos, globs = OUT.outputDistributor(outdict, prev_scaff, next_pos, outfile, fastqfile, fastafile, globs);
				# for outdict in outdicts:
				# 	prev_scaff, next_pos, globs = OUT.outputDistributor(outdict, prev_scaff, next_pos, outfile, fastqfile, fastafile, globs);
				cur_lines, outdicts = [], [];
				step_start_time = RC.report_step(globs, step, step_start_time, "Success!");
		# Read the input file line by line. Once a certain number of lines have been read, pass them to siteParse in parallel.

		if cur_lines != []:
			step = "Processing lines "  + str(i_start) + "-" + str(i);
			step_start_time = RC.report_step(globs, step, False, "In progress...");

			line_chunks = list(RC.chunks(cur_lines, globs['lines-per-proc']));
			for result in pool.starmap(CALC.refCalc, ((line_chunk, globs) for line_chunk in line_chunks)):
				#outdicts += result;
				for outdict in result:
					# print(site);
					# print(result[site]);
					prev_scaff, next_pos, globs = OUT.outputDistributor(outdict, prev_scaff, next_pos, outfile, fastqfile, fastafile, globs);
			# for outdict in outdicts:
			# 	prev_scaff, next_pos, globs = OUT.outputDistributor(outdict, prev_scaff, next_pos, outfile, fastqfile, fastafile, globs);	
			step_start_time = RC.report_step(globs, step, step_start_time, "Success!");
		# Read the input file line by line. Once a certain number of lines hav
		# Count the last chunk of lines if necessary.

		if next_pos <= globs['scaff-lens'][prev_scaff]:
			step = "Filling final unmapped positions"
			step_start_time = RC.report_step(globs, step, False, "In progress...");
			seq = RC.fastaGet(globs['ref-file'], globs['ref'][prev_scaff])[1];
			outdict = { 'scaff' : prev_scaff, 'pos' : globs['scaff-lens'][prev_scaff], 'ref' : seq[next_pos-1], 
                        'rq' : -2, 'raw' : "NA", 'lr' : "NA", 'l_match' : "NA", 
                        'l_mismatch' : "NA", 'gls' : "NA", 'cor_ref' : "NA", 
                        'cor_score' : "NA", 'cor_raw' : "NA" };
			prev_scaff, next_pos, globs = OUT.outputDistributor(outdict, prev_scaff, next_pos, outfile, fastqfile, fastafile, globs);
			step_start_time = RC.report_step(globs, step, step_start_time, "Success!");
		# If the last positions are unmapped they won't have been filled in. Do that here using the last position (length) of the
		# previous scaffold as the outdict.

		globs['scaffs-written'].append(prev_scaff);

		step = "Checking for unmapped scaffolds"
		step_start_time = RC.report_step(globs, step, False, "In progress...");
		for scaff in globs['scaff-lens']:
			if scaff not in globs['scaffs-written']:
				scaff_len = globs['scaff-lens'][scaff];
				seq = RC.fastaGet(globs['ref-file'], globs['ref'][scaff])[1];
				for p in range(len(seq)):
					pos = p + 1;
					ref = seq[p]
					outdict = { 'scaff' : scaff, 'pos' : pos, 'ref' : ref, 
								'rq' : -2, 'raw' : "NA", 'lr' : "NA", 'l_match' : "NA", 
								'l_mismatch' : "NA", 'gls' : "NA", 'cor_ref' : "NA", 
								'cor_score' : "NA", 'cor_raw' : "NA" };
					prev_scaff, next_pos, globs = OUT.outputDistributor(outdict, scaff, next_pos, outfile, fastqfile, fastafile, globs);
		step_start_time = RC.report_step(globs, step, step_start_time, "Success!");
		# If any scaffolds had no positions with reads mapped, they will not have been written. Go through them here to write out
		# their positions in ouput files with scores of -2.

		if globs['fastq-opt']:
			fastqfile.close();
		# Close the FASTQ file if --fastq was set.

		if globs['fasta-opt']:
			fastafile.close();
		# Close the FASTA file if --fasta was set.

		if globs['bed-opt']:
			step = "Writing final bed file"
			step_start_time = RC.report_step(globs, step, False, "In progress...");
			OUT.outputBed(globs['cur-bed']);
			step_start_time = RC.report_step(globs, step, step_start_time, "Success!");
		# Write out the last bed file.

		with open(globs['out-summary'], "w") as sumout:
			sumout.write("# SCAFFOLDS:\t" + str(globs['num-scaff']) + "\n");
			sumout.write("# POSITIONS:\t" + str(globs['num-pos']) + "\n");
			sumout.write("# UNMAPPED POSITIONS:\t" + str(globs['hist'][2]['count']) + "\n");
			if globs['correct-opt']:
				sumout.write("# ERRORS CORRECTED:\t" + str(globs['num-corrected']) + "\n");
				err_rate = globs['num-corrected'] / globs['num-pos'];
				sumout.write("# ERROR RATE PER BASE:\t" + str(err_rate) + "\n");

				sumout.write("#\n# ERROR TYPES\n");
				sumout.write("from\tto\tcount\n");
				for err in globs['err-types']:
					outline = err[0] + "\t" + err[1] + "\t" + str(globs['err-types'][err]);
					sumout.write(outline + "\n");
				
			sumout.write("#\n# SCORE DISTRIBUTION\n");
			sumout.write("bin\tcount\n");
			for score_bin in globs['hist']:
				outline = [ globs['hist'][score_bin]['min'], globs['hist'][score_bin]['max'], globs['hist'][score_bin]['count'] ];
				outline = [ str(o) for o in outline ];
				if outline[0] == outline[1]:
					outline = outline[0] + "\t" + outline[2];
				else: 
					outline = outline[0] + "-" + outline[1] + "\t" + outline[2];
				sumout.write(outline + "\n");
		# Write the summary file.

	return;
#############################################################################

if __name__ == '__main__':
# Main is necessary for multiprocessing to work on Windows.
	globs = GV.init();
	
	if any(v in sys.argv for v in ["--version", "-version", "--v", "-v"]):
		print("# Referee version " + globs['version'] + " released on " + globs['releasedate'])
		sys.exit(0);
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

