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
	parser.add_argument("-c", dest="score_cutoff", help="The cut-off score for --correct. Sites that score below this cut-off will have an alternate reference base suggested. If --correct isn't set, this option is ignored. Default: 1", type=int, default=1);
	parser.add_argument("-p", dest="processes", help="The number of processes Referee should use. Default: 1.", type=int, default=1);

	parser.add_argument("-v", dest="verbosity", help="An option to control the amount of output printed to the screen. -1: print nothing. 0: print only some log info. 1 (default): print some detailed output for each reconciliation (this detailed output is also available by default in the _det output file).", type=int, default=1);
	parser.add_argument("--tests", dest="test_opt", help="Use 'grampa.py --tests' the first time you run grampa to run through all the options with pre-set input files.", action="store_true");
	parser.add_argument("--stats", dest="stats_opt", help=argparse.SUPPRESS, action="store_true");

	args = parser.parse_args();
	# The input options and help messages

	if args.test_opt:
		RC.testPrep();
		sys.exit();
	# Call of the tests script if --tests is set.

	file_paths = {};

	if not args.input_list and (not args.gl_file and not args.ref_file):
		RC.errorOut(1, "No input method specified. Make sure one input method (either just -i or both -gl and -ref) is specified.");
	# Make sure at least one input method has been specified (either -i or -gl + -ref).

	if args.input_list:
	# If the input method is -i
		if args.gl_file or args.ref_file:
			RC.errorOut(2, "With -i specified, -gl and -ref should not be specified.");
		if not os.path.isfile(args.input_list):
			RC.errorOut(3, "Cannot find file specified by -i.");
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
				RC.errorOut(4, "Invalid file path found in input file on following line: " + line.strip());
			if not SeqIO.parse(cur_ref_file, "fasta"):
				RC.errorOut(5, "Cannot read the following as FASTA file: " + cur_ref_file);
			cur_outfile = cur_gl_file + "-referee-out.txt";
			file_paths[cur_gl_file] = [cur_ref_file, cur_outfile];
		# Read the input file and get all the file paths. Also specify output file paths.

	else:
	# If the input method is -gl and -ref
		if not os.path.isfile(args.ref_file):
			RC.errorOut(6, "Cannot find reference genome file specified by -ref.");
		if not SeqIO.parse(args.ref_file, "fasta"):
			RC.errorOut(7, "Cannot read file specified by -ref as FASTA file.");

		if not args.out_dest:
			outfile = "referee-out.txt";
		else:
			outfile = args.out_dest;

		file_paths[args.gl_file] = [args.ref_file, outfile];


	if args.verbosity not in [-2,-1,0,1]:
		RC.errorOut(8, "-v must take values of -1, 0, or 1");
	else:
		globs.v = args.verbosity;
	# Checking the verbosity option.

	return file_paths;

	### Begin output prep block.
	# outdir = os.path.normpath(args.output_dir);
	# # Initialize output directory and files.

	# globs.spec_type = 'm' if args.spec_tree_type else 's';
	# # The rest of the code still uses the old --multree (-t) formatting for spec_type.
	# globs.num_procs = args.processes;
	# globs.label_opt = args.label_opt;
	# globs.mul_opt = args.mul_opt;
	# globs.check_nums = args.check_nums;
	# globs.maps_opt = args.maps_opt;
	# globs.orth_opt = args.orth_opt;
	# globs.stats = args.stats_opt;
	# if args.verbosity == -2:
	# 	globs.stats = False;

	# # Setting a few global (read-only) variables based on the input options.

	# if not args.label_opt:
	# 	if os.path.isdir(outdir):
	# 		outdir_suffix = 1;
	# 		outdir_prefix = outdir;
	# 		while os.path.isdir(outdir):
	# 			outdir = outdir_prefix + "-" + str(outdir_suffix);
	# 			outdir_suffix += 1;
	# 	os.system("mkdir " + outdir);
	# 	globs.output_directory = outdir;
	# 	# Making the output directory

	# 	globs.outfilename = os.path.join(outdir, args.output_prefix + "_out.txt");
	# 	RC.filePrep(globs.outfilename);
	# 	# Preparing the main output file
	# 	globs.gene_file_filtered = os.path.join(outdir, args.output_prefix + "_trees_filtered.txt");
	# 	if globs.lca_opt != 1:
	# 		if args.groups_dir == None:
	# 			globs.pickle_dir = os.path.join(outdir, "groups_dir");
	# 			os.system("mkdir " + globs.pickle_dir);
	# 		elif os.path.isdir(args.groups_dir):
	# 			globs.pickle_dir = args.groups_dir;
	# 		else:
	# 			RC.errorOut(6, "Cannot find specified groups directory! (-r)");
	# 	if not args.mul_opt:
	# 		globs.checkfilename = os.path.join(outdir, args.output_prefix + "_checknums.txt");
	# 		RC.filePrep(globs.checkfilename, "# GT/MT combo\t# Groups\t# Fixed\t# Combinations\n");
	# 		# Filtered gene trees file, groups file, and checknums file.

	# 		if not args.check_nums:
	# 			globs.detoutfilename = os.path.join(outdir, args.output_prefix + "_det.txt");
	# 			RC.filePrep(globs.detoutfilename);
	# 		# If --checknum is not set, we have to prepare detailed output file.

	# 			if args.orth_opt:
	# 				globs.labeled_tree_file = os.path.join(outdir, args.output_prefix + "_labeled_trees.txt");
	# 				globs.orth_file_name = os.path.join(outdir, args.output_prefix + "_orthologies.txt");
	# 			# The orthology output files.
	# ### End output prep block.

	# return args.spec_tree, args.gene_input, args.h1_spec, args.h2_spec;


