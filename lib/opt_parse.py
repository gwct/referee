import sys, os, refcore as RC, global_vars as globs
from Bio import SeqIO
#############################################################################

def optParse(errorflag):
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


	parser.add_argument("-o", dest="out_dest", help="A name for the output location. If input is specified with -ref and -gl, this will be the name of a single file. If input is specified by -i, this will be the name of a directory which will be made for you. Default: referee-out", default=False);
	parser.add_argument("--fastq", dest="fastq_flag", help="Set this option to output in FASTQ format instead of the default tab delimited format.", action="store_true", default=False);
	parser.add_argument("--correct", dest="correct_flag", help="Set this option to allow Referee to suggest alternate reference bases for sites that score below a cut-off set by -c.", action="store_true", default=False);
	parser.add_argument("-c", dest="score_cutoff", help="The cut-off score for --correct. Sites that score below this cut-off will have an alternate reference base suggested. If --correct isn't set, this option is ignored. Default: 1", default=False);
	parser.add_argument("-p", dest="processes", help="The number of processes Referee should use. Default: 1.", default=False);

	parser.add_argument("-v", dest="verbosity", help="An option to control the amount of output printed to the screen. -1: print nothing. 0: print only some log info. 1 (default): print some detailed output for each reconciliation (this detailed output is also available by default in the _det output file).", type=int, default=1);
	parser.add_argument("--tests", dest="test_opt", help="Use 'grampa.py --tests' the first time you run grampa to run through all the options with pre-set input files.", action="store_true");
	parser.add_argument("--stats", dest="stats_opt", help=argparse.SUPPRESS, action="store_true");

	args = parser.parse_args();
	# The input options and help messages

	if args.test_opt:
		RC.testPrep();
		sys.exit();
	# Call of the tests script if --tests is set.

	if args.processes and not args.processes.isdigit():
		RC.errorOut(1, "-p must be an integer value greater than 1.");
	elif args.processes:
		globs.num_procs = int(args.processes);
	# Checking the number of processors option.

	out_ext = ".txt";
	if args.fastq_flag:
		globs.fastq = True;
		out_ext = ".fq";
	# Checking the fastq option.		

	file_paths = {};

	if not args.input_list and (not args.gl_file and not args.ref_file):
		RC.errorOut(2, "No input method specified. Make sure one input method (either just -i or both -gl and -ref) is specified.");
	# Make sure at least one input method has been specified (either -i or -gl + -ref).

	if args.input_list:
	# If the input method is -i
		if args.gl_file or args.ref_file:
			RC.errorOut(3, "With -i specified, -gl and -ref should not be specified.");
		if not os.path.isfile(args.input_list):
			RC.errorOut(4, "Cannot find file specified by -i.");
		# Make sure only -i is specified and that we can find the file.

		if not args.out_dest:
			outdir = "referee-out-" + globs.startdatetime;
		else:
			outdir = args.out_dest;
		if not os.path.isdir(outdir):
			print(" + Making output directory: " + outdir);
			os.system("mkdir \"" + outdir + "\"");
		# Specifiy and create the output directory, if necessary.

		for line in open(args.input_list):
			cur_gl_file, cur_ref_file = line.strip().split("\t");
			if not os.path.isfile(cur_gl_file) or not os.path.isfile(cur_ref_file):
				RC.errorOut(5, "Invalid file path found in input file on following line: " + line.strip());
			if not SeqIO.parse(cur_ref_file, "fasta"):
				RC.errorOut(6, "Cannot read the following as FASTA file: " + cur_ref_file);
			cur_outfile = cur_gl_file + "-referee-out" + out_ext;
			file_paths[cur_gl_file] = [cur_ref_file, cur_outfile];
		# Read the input file and get all the file paths. Also specify output file paths.

	else:
	# If the input method is -gl and -ref
		if not os.path.isfile(args.ref_file):
			RC.errorOut(7, "Cannot find reference genome file specified by -ref.");
		if not SeqIO.parse(args.ref_file, "fasta"):
			RC.errorOut(8, "Cannot read file specified by -ref as FASTA file.");
		# Check if the reference file is a valid FASTA file.

		if not os.path.isfile(args.gl_file):
			RC.errorOut(9, "Cannot find genotype likelihood file specified by -gl.");
		# Check if the genotype likelihood file is a valid file.

		if not args.out_dest:
			outfile = "referee-out-" + globs.startdatetime + out_ext;
		else:
			outfile = args.out_dest;
		# Specify the output file.

		file_paths[args.gl_file] = [args.ref_file, outfile];
		# Get the file paths for the current files.

	if args.verbosity not in [-2,-1,0,1]:
		RC.errorOut(10, "-v must take values of -1, 0, or 1");
	else:
		globs.v = args.verbosity;
	# Checking the verbosity option.

	return file_paths;

	