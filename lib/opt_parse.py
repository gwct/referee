import sys, os, refcore as RC
from Bio import SeqIO
#############################################################################

def optParse(globs):
# This function handles the command line options and prepares the output directory and files.
	try:
		import argparse;
	except:
		sys.exit("\n*** ERROR: Your installation of Python is missing the argparse module. Please try a different version of Python (2.7 or later) or install the module.\n")
	# First check if the argparse module is installed. If not, the input options cannot be parsed.

	parser = argparse.ArgumentParser(description="Referee: Reference genome quality scoring.");

	parser.add_argument("-ref", dest="ref_file", help="The FASTA assembly to which you have mapped your reads.", default=False);
	parser.add_argument("-gl", dest="gl_file", help="The file containing the genotype likelihood calculations.", default=False);
	parser.add_argument("-i", dest="input_list", help="A file containing the paths to multiple input files containing genotype likelihoods and their reference FASTA files. Each line should contain one genotype likelihood file path and one FASTA file path separated by a tab.", default=False);
	# Inputs
	parser.add_argument("-o", dest="out_dest", help="A name for the output location. If input is specified with -ref and -gl, this will be the name of a single file. If input is specified by -i, this will be the name of a directory which will be made for you. Default: referee-out-[date]-[time]", default=False);
	# Output
	parser.add_argument("--fastq", dest="fastq_flag", help="Set this option to output in FASTQ format instead of the default tab delimited format.", action="store_true", default=False);
	parser.add_argument("--correct", dest="correct_flag", help="Set this option to allow Referee to suggest alternate reference bases for sites that score below a cut-off set by -c.", action="store_true", default=False);
	parser.add_argument("--mapped", dest="mapped_flag", help="Set this to calculate scores only for positions that have reads mapped to them.", action="store_true", default=False);
	# User options	
	#parser.add_argument("-s", dest="startpos", help="Set the starting position for the input file(s). Default: 1", default=False);
	#parser.add_argument("-e", dest="endpos", help="Set the end position for the input file(s). Default: last position in assembly/scaffold", default=False);
	parser.add_argument("-c", dest="score_cutoff", help="The cut-off score for --correct. Sites that score below this cut-off will have an alternate reference base suggested. If --correct isn't set, this option is ignored. Default: 1", default=False);
	parser.add_argument("-p", dest="processes", help="The number of processes Referee should use. Not that 1 process is always reserved for the main script, so to see any benefit you must enter 3 or above. Default: 1.", default=False);
	# User params
	parser.add_argument("--stats", dest="stats_opt", help=argparse.SUPPRESS, action="store_true", default=False);
	parser.add_argument("--debug", dest="debug_opt", help=argparse.SUPPRESS, action="store_true", default=False);
	# Debug and performance tests

	args = parser.parse_args();
	# The input options and help messages

	if args.processes and not args.processes.isdigit():
		RC.errorOut(1, "-p must be an integer value greater than 1.", globs);
	elif args.processes:
		globs['num-procs'] = int(args.processes)-1;
	# Checking the number of processors option.

	out_ext = ".txt";
	if args.fastq_flag:
		globs['fastq'] = True;
		out_ext = ".fq";
		RC.printWrite(globs['logfilename'], globs['log-v'], "# --fastq : Output format is FASTQ.");
	else:
		RC.printWrite(globs['logfilename'], globs['log-v'], "# Output format is tab delimited.");
	# Checking the fastq option.

	if args.mapped_flag:
		globs['mapped'] = True;
		RC.printWrite(globs['logfilename'], globs['log-v'], "# --mapped : Only calculating scores for positions with reads mapped to them.");
	else:
		RC.printWrite(globs['logfilename'], globs['log-v'], "# Calculating scores for every reference position specified.");
	# Checking the fastq option.

	if args.correct_flag:
		if args.score_cutoff and not args.score_cutoff.isdigit():
			RC.errorOut(2, "-c must be an integer value greater than 1.", globs);
		elif args.score_cutoff:
			globs['correct-cutoff'] = int(args.score_cutoff);
		RC.printWrite(globs['logfilename'], globs['log-v'], "# --correct : Suggesting higher scoring alternative base when reference scores below: " + str(globs.correct_cutoff) +".");
		globs['correct-opt'] = True;
	# Checking the correct option.

	if args.stats_opt:
		import psutil
		globs['stats'] = True;
		globs['pids'] = [psutil.Process(os.getpid())];		
		globs['progstarttime'] = RC.report_stats(globs, stat_start=True);
		globs['stepstarttime'] = globs['progstarttime'];
	# Initializing if --stats is set.

	if args.debug_opt:
		RC.printWrite(globs['logfilename'], globs['log-v'], "# --debug : Using tab delimited output and reporting extra columns.");
		globs['debug'] = True;
		globs['fastq'] = False;
		out_ext = ".txt";
	# Parse debug and stats options. Note: debug only compatible with tab delimited output.

	if globs['stats']:
		globs['stepstartime'] = RC.report_stats(globs, "Get scaff lengths");
	globs['scaff-lens'] = RC.getScaffLens(args.ref_file);

	file_paths, file_num = {}, 1;

	if not args.input_list and (not args.gl_file and not args.ref_file):
		RC.errorOut(3, "No input method specified. Make sure one input method (either just -i or both -gl and -ref) is specified.", globs);
	# Make sure at least one input method has been specified (either -i or -gl + -ref).

	if args.input_list:
	# If the input method is -i
		if args.gl_file or args.ref_file:
			RC.errorOut(4, "With -i specified, -gl and -ref should not be specified.", globs);
		if not os.path.isfile(args.input_list):
			RC.errorOut(5, "Cannot find file specified by -i.", globs);
		# Make sure only -i is specified and that we can find the file.

		if not args.out_dest:
			outdir = "referee-out-" + globs['startdatetime'];
		else:
			outdir = args.out_dest;
		if not os.path.isdir(outdir):
			RC.printWrite(globs['logfilename'], globs['log-v'], "+ Making output directory: " + outdir);
			os.system("mkdir \"" + outdir + "\"");
		# Specifiy and create the output directory, if necessary.

		for line in open(args.input_list):
			if line.strip():
				continue;
			tmpline = line.strip().split("\t");
			if len(line) == 2:
				cur_gl_file, cur_ref_file = tmpline;
			else:
				RC.errorOut(5, "Could not read the following line of the input file: " + line, globs);

			if not os.path.isfile(cur_gl_file) or not os.path.isfile(cur_ref_file):
				RC.errorOut(6, "Invalid file path found in input file on following line: " + line.strip(), globs);
			if not SeqIO.parse(cur_ref_file, "fasta"):
				RC.errorOut(7, "Cannot read the following as FASTA file: " + cur_ref_file, globs);
			cur_outfile = cur_gl_file + "-referee-out" + out_ext;

			if globs['stats']:
				globs['stepstartime'] = RC.report_stats(globs, "Get scaff ids");
			file_paths[file_num] = { 'in' : cur_gl_file, 'ref' : cur_ref_file, 'out' : cur_outfile,
										'scaffs' : RC.getScaffs(cur_gl_file), 'start' : False, 'stop' : False };
		# Read the input file and get all the file paths. Also specify output file paths.

	else:
	# If the input method is -gl and -ref
		if not os.path.isfile(args.ref_file):
			RC.errorOut(8, "Cannot find reference genome file specified by -ref.", globs);
		if not SeqIO.parse(args.ref_file, "fasta"):
			RC.errorOut(9, "Cannot read file specified by -ref as FASTA file.", globs);
		# Check if the reference file is a valid FASTA file.

		if not os.path.isfile(args.gl_file):
			RC.errorOut(10, "Cannot find genotype likelihood file specified by -gl.", globs);
		# Check if the genotype likelihood file is a valid file.

		if not args.out_dest:
			outfile = "referee-out-" + globs['startdatetime'] + out_ext;
		else:
			outfile = args.out_dest;
		# Specify the output file.

		if globs['stats']:
			globs['stepstartime'] = RC.report_stats(globs, "Get scaff ids");
		file_paths[file_num] = { 'in' : args.gl_file, 'ref' : args.ref_file, 'out' : outfile,
								'scaffs' : RC.getScaffs(args.gl_file), 'start' : False, 'stop' : False };
	# Get the file paths for the current files.

	for i in file_paths:
		file_paths[i]['globs'] = globs;
	return file_paths;

#############################################################################

def multiPrep(files):
	import math

	file_info = files[1];
	globs = file_info['globs'];
	#infilename, reffilename, outfilename, scaffs, globs = files[1];
	RC.printWrite(globs['logfilename'], globs['log-v'],"+ Making tmp directory: " + globs['tmpdir']);
	os.system("mkdir " + globs['tmpdir']);
	# Make the temporary directory to store the split files and split outputs.

	if len(file_info['scaffs']) == 1:
		new_files = {};
		tmpfiles = [os.path.join(globs['tmpdir'], str(i) + ".txt") for i in range(globs['num-procs'])];
		num_pos = RC.getFileLen(file_info['in']);

		pospersplit = int(math.ceil(num_pos / float(globs['num-procs'])));
		with open(file_info['in'], "r") as infile:
			cur_scaffs = [];
			file_num, file_pos = 0, 0;
			tmpfile = open(tmpfiles[file_num], "w");
			for line in infile:
				tmpline = line.strip().split("\t");
				scaff, pos = tmpline[0], int(tmpline[1]);
				if scaff not in cur_scaffs:
					cur_scaffs.append(scaff);
				tmpfile.write(line);
				file_pos += 1;
				if file_pos >= pospersplit:
					tmpfile.close();
					newoutfile = os.path.join(globs['tmpdir'], str(file_num) + "-out.txt");
					new_files[file_num] = { 'in' : tmpfiles[file_num], 'ref' : file_info['ref'], 'out' : newoutfile, 
											'scaffs' : cur_scaffs, 'start' : False, 'stop' : False, 'globs' : globs };
					file_pos = 0;
					file_num += 1;
					if file_num != len(tmpfiles):
						tmpfile = open(tmpfiles[file_num], "w");

		if len(new_files) != len(tmpfiles):
			tmpfile.close();
			newoutfile = os.path.join(globs['tmpdir'], str(file_num) + "-out.txt");
			new_files[file_num] = { 'in' : tmpfiles[file_num], 'ref' : file_info['ref'], 'out' : newoutfile, 
									'scaffs' : cur_scaffs, 'start' : False, 'stop' : False, 'globs' : globs };

	else:
		new_files = {};
		tmpfiles = { scaff : os.path.join(globs['tmpdir'], scaff + ".txt") for scaff in file_info['scaffs'] };

		last_scaff = file_info['scaffs'][0];
		tmpfile = open(tmpfiles[last_scaff], "w");
		file_num = 1;
		with open(file_info['in'], "r") as infile:
			for line in infile:
				cur_scaff = line.split("\t")[0];
				if cur_scaff != last_scaff:
					tmpfile.close();
					newoutfile = os.path.join(globs['tmpdir'], last_scaff + "-out.txt");
					new_files[file_num] = { 'in' : tmpfiles[file_num], 'ref' : file_info['ref'], 'out' : newoutfile, 
											'scaffs' : cur_scaffs, 'start' : False, 'stop' : False, 'globs' : globs };					
					file_num += 1;
					tmpfile = open(tmpfiles[cur_scaff], "w");
				tmpfile.write(line);
				last_scaff = cur_scaff;

		tmpfile.close();
		newoutfile = os.path.join(globs['tmpdir'], last_scaff + "-out.txt");
		new_files[file_num] = { 'in' : tmpfiles[file_num], 'ref' : file_info['ref'], 'out' : newoutfile, 
								'scaffs' : cur_scaffs, 'start' : False, 'stop' : False, 'globs' : globs };

	return new_files;