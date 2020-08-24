#############################################################################
# Old or supplemental code that didn't end up being in the program


#############################################################################
# INITIAL ATTEMPT TO PARALLELIZE BY SPITTING FILES INTO CHUNKS
# def multiPrep(files):
# 	import math

# 	file_info = files[1];
# 	globs = file_info['globs'];
# 	#infilename, reffilename, outfilename, scaffs, globs = files[1];
# 	RC.printWrite(globs['logfilename'], globs['log-v'],"+ Making tmp directory: " + globs['tmpdir']);
# 	os.system("mkdir " + globs['tmpdir']);
# 	# Make the temporary directory to store the split files and split outputs.

# 	if len(file_info['scaffs']) == 1:
# 		new_files = {};
# 		tmpfiles = [os.path.join(globs['tmpdir'], str(i) + ".txt") for i in range(globs['num-procs'])];
# 		num_pos = RC.getFileLen(file_info['in']);

# 		pospersplit = int(math.ceil(num_pos / float(globs['num-procs'])));
# 		with open(file_info['in'], "r") as infile:
# 			cur_scaffs = [];
# 			file_num, file_pos = 0, 0;
# 			tmpfile = open(tmpfiles[file_num], "w");
# 			for line in infile:
# 				tmpline = line.strip().split("\t");
# 				scaff, pos = tmpline[0], int(tmpline[1]);
# 				if scaff not in cur_scaffs:
# 					cur_scaffs.append(scaff);
# 				tmpfile.write(line);
# 				file_pos += 1;
# 				if file_pos >= pospersplit:
# 					tmpfile.close();
# 					newoutfile = os.path.join(globs['tmpdir'], str(file_num) + "-out.txt");
# 					new_files[file_num] = { 'in' : tmpfiles[file_num], 'ref' : file_info['ref'], 'out' : newoutfile, 
# 											'scaffs' : cur_scaffs, 'start' : False, 'stop' : False, 'globs' : globs };
# 					file_pos = 0;
# 					file_num += 1;
# 					if file_num != len(tmpfiles):
# 						tmpfile = open(tmpfiles[file_num], "w");

# 		if len(new_files) != len(tmpfiles):
# 			tmpfile.close();
# 			newoutfile = os.path.join(globs['tmpdir'], str(file_num) + "-out.txt");
# 			new_files[file_num] = { 'in' : tmpfiles[file_num], 'ref' : file_info['ref'], 'out' : newoutfile, 
# 									'scaffs' : cur_scaffs, 'start' : False, 'stop' : False, 'globs' : globs };

# 	else:
# 		new_files = {};
# 		tmpfiles = { scaff : os.path.join(globs['tmpdir'], scaff + ".txt") for scaff in file_info['scaffs'] };

# 		last_scaff = file_info['scaffs'][0];
# 		tmpfile = open(tmpfiles[last_scaff], "w");
# 		file_num = 1;
# 		with open(file_info['in'], "r") as infile:
# 			for line in infile:
# 				cur_scaff = line.split("\t")[0];
# 				if cur_scaff != last_scaff:
# 					tmpfile.close();
# 					newoutfile = os.path.join(globs['tmpdir'], last_scaff + "-out.txt");
# 					new_files[file_num] = { 'in' : tmpfiles[file_num], 'ref' : file_info['ref'], 'out' : newoutfile, 
# 											'scaffs' : cur_scaffs, 'start' : False, 'stop' : False, 'globs' : globs };					
# 					file_num += 1;
# 					tmpfile = open(tmpfiles[cur_scaff], "w");
# 				tmpfile.write(line);
# 				last_scaff = cur_scaff;

# 		tmpfile.close();
# 		newoutfile = os.path.join(globs['tmpdir'], last_scaff + "-out.txt");
# 		new_files[file_num] = { 'in' : tmpfiles[file_num], 'ref' : file_info['ref'], 'out' : newoutfile, 
# 								'scaffs' : cur_scaffs, 'start' : False, 'stop' : False, 'globs' : globs };

# 	return new_files;

#############################################################################
# IF I WANTED TO NUMBER THE STEPS
# def printStep(step, msg):
# # Prints a message and increments a counter.
# 	if globs.v not in [-2,-1]:
# 		print(msg);
# 	return step+1;

#############################################################################
# IF I NEEDED TO CHECK THE OS
# def osCheck(test_cmd):
# # For the tests script. Need to know if we are on Windows in order to pass the command correctly.
# 	import platform
# 	if platform.system == 'Windows':
# 		test_cmd = " ".join(test_cmd);
# 	return test_cmd;

#############################################################################
# A WAY TO GET A FASTA SEQUENCE BASED ON TITLE USING BIOPYTHON
# from Bio import SeqIO
# def getFastaInfo(ref_file, scaff_id):
# 	for record in SeqIO.parse(ref_file, "fasta"):
# 		if record.id == scaff_id:
# 			seq = record.seq;
# 			seqlen = len(record.seq);
# 			break;
# 	return seq, seqlen;

#############################################################################
# A WAY TO GET SEQUENCE LENGTHS USING BIOPYTHON
# def getScaffLens(ref_file):
# 	cur_lens = {};
# 	for record in SeqIO.parse(ref_file, "fasta"):
# 		cur_lens[record.id] = len(record.seq);
# 	return cur_lens;

#############################################################################
# A WAY TO GET ALL THE TITLES IN A FASTA FILE
# def getScaffs(i_name):
# 	scaffs = [];
# 	try:
# 		gzip_check = gzip.open(i_name).read(1);
# 		reader = gzip.open;
# 	except:
# 		reader = open;
# 	# Check if the genotype likelihood file is gzipped, and if so set gzip as the file reader. Otherwise, read as a normal text file.
# 	for line in reader(i_name):
# 		scaff = line.split("\t")[0];
# 		if scaff not in scaffs:
# 			scaffs.append(scaff);
# 	return scaffs;

#############################################################################
# GETS THE NUMBER OF LINES IN A FILE
# def getFileLen(i_name):
# 	num_lines = 0;
# 	for line in open(i_name).xreadlines(): num_lines += 1;
# 	return float(num_lines);

#############################################################################
# THE ORIGINAL SCORE CALCULATION FUNCTION WHEN I WAS PARALLELIZING BY CHUNKS
# def refCalc(file_item):
#     gl_file, ref_file, outfilename = file_item[1]['in'], file_item[1]['ref'], file_item[1]['out'];
#     scaffs, start, stop = file_item[1]['scaffs'], file_item[1]['start'], file_item[1]['stop'];
#     globs = file_item[1]['globs'];

#     genotypes = ["AA", "AC", "AG", "AT", "CC", "CG", "CT", "GG", "GT", "TT"]
#     last_scaff, cor_ref, cor_score, scaff_pos = "", "", "", 1;

#     if globs['fastq']:
#         fq_seq, fq_scores, fq_curlen, fq_lastpos = [], [], 0, 1;
#     # Variables for FASTQ output.

#     with open(outfilename, "w") as outfile:
#         try:
#             gzip_check = gzip.open(gl_file).read(1);
#             reader = gzip.open;
#         except:
#             reader = open;
#         # Check if the genotype likelihood file is gzipped, and if so set gzip as the file reader. Otherwise, read as a normal text file.

#         for line in reader(gl_file):
#             line = line.strip().split("\t");
#             scaff, pos, gl_list = line[0], int(line[1]), line[2:];

#             if start:
#                 start_scaff, start_pos = start;
#                 if start_scaff == scaff and pos < start_pos:
#                     continue;

#             if stop:
#                 stop_scaff, stop_pos = stop;

#             if scaff != last_scaff:
#                 seq, seqlen = RC.getFastaInfo(ref_file, scaff);
#             last_scaff = scaff;
#             # If the scaffold of the current line is different from the last scaffold, retrieve the sequence.

#             if not globs['mapped']:
#                 while scaff_pos != pos:
#                     scaff_ref = seq[scaff_pos-1];
#                     if globs['fastq']:
#                         fq_seq, fq_scores, fq_curlen, fq_lastpos = OUT.outputFastq(outfile, scaff, scaff_pos, scaff_ref, -2, fq_seq, fq_scores, fq_curlen, fq_lastpos, globs);
#                     else:
#                         OUT.outputTab(outfile, scaff, str(scaff_pos), scaff_ref, -2, "NA", "NA", "NA", "NA", globs, cor_base=cor_ref, cor_score=cor_score);
#                     scaff_pos += 1;

#                     if stop and stop_scaff == scaff and scaff_pos == stop_pos:
#                         break;
#             # If the current position has skipped ahead from where we are in the scaffold, that means there are
#             # intervening positions with no reads mapped. This fills in those scores as -2.

#             if stop and stop_scaff == scaff and scaff_pos == stop_pos:
#                 break;

#             gls = { genotypes[x] : math.exp(float(gl_list[x])) for x in range(len(gl_list)) };
#             # Parse the info from the current line -- scaffold, position, genotype likelihoods.

#             ref = seq[pos-1];
#             # Gets the called reference base at the current position.

#             rq, lr, l_match, l_mismatch = calcScore(ref, gls);
#             # Call the scoring function.

#             if globs['correct-opt']:
#                 cor_ref, cor_score = correctRef(rq, ref, gls);        

#             if globs['fastq']:
#                 fq_seq, fq_scores, fq_curlen, fq_lastpos = OUT.outputFastq(outfile, scaff, pos, ref, rq, fq_seq, fq_scores, fq_curlen, fq_lastpos, globs);
#             else:
#                 OUT.outputTab(outfile, scaff, str(pos), ref, rq, lr, l_match, l_mismatch, gls, globs, cor_base=cor_ref, cor_score=cor_score);
#             scaff_pos += 1;
#             # Write the score to the output file and iterate the scaff_pos.

#         if globs['fastq']:
#             fq_seq, fq_scores, fq_curlen, fq_lastpos = OUT.outputFastq(outfile, scaff, pos, ref, rq, fq_seq, fq_scores, fq_curlen, fq_lastpos, globs, final=True);

#############################################################################

# print pos, len(RC.fastaGet(globs['reffile'], globs['ref'][scaff])[1]), globs['reffile']
# print RC.fastaGet(globs['reffile'], globs['ref'][scaff])[1]
# print RC.fastaGet(globs['reffile'], globs['ref'][scaff])[1][pos-1];
# SOME LINES FOR CHECKING THE FASTA READER IN ref_calc BEFORE ASSIGNING ref.

# ref = ref_ind[scaff].seq[pos-1];
# READS THE ref IF USING BIOPYTHON.

#############################################################################
# THE PARALLELIZATION TEST SCRIPT

# import sys, os, multiprocessing as mp, lib.ref_calc as CALC, lib.ref_out as OUT

# def testFunc2(x):
#     return 3;

# def testFunc(it):
#     x, c = it;
#     y = testFunc2(x)
#     return {1 : x, 2 : c, 3 : y};

# def testPrint(x, c):
# 	print(x[1]);

# infilename = 'data/angsd-output-snippet.txt';
# #f = open(infilename, "r");
# #for line in f.iteritems():
# #    print line;

# if __name__ == '__main__':
#     procs = 4;
#     pool = mp.Pool(processes = procs);
#     #f = open(infilename, "r")
#     c = {1 : "A", 2 : "B", 3 : "C"}
#     with open(infilename, "r") as infile:
#         for outt in pool.map(CALC.testFunc, ((line, c) for line in infile)):
#             print outt;
#             OUT.testPrint(outt, c);
#             #print result;   

#############################################################################
# THE LINE-BY-LINE PARALLELIZATION WHICH TURNED OUT TO BE TOO SLOW.

	# 	with reader(files[file_num]['in'], "r") as infile, open(files[file_num]['out'], "w") as outfile:
	# 		if globs['num-procs'] == 1:
	# 			for line in infile:
	# 				outdict = CALC.refCalc((line, globs));
	# 				OUT.outputTab(outdict, outfile, globs);
	# 		# A serial version.
	# 		else:
	# 			pool = mp.Pool(processes = globs['num-procs']);

	# 			if globs['stats']:
	# 				for result in pool.imap(RC.getSubPID, range(globs['num-procs'])):
	# 					globs['pids'].append(result);
	# 			for outdict in pool.imap(CALC.refCalc, ((line, globs) for line in infile)):
	# 				OUT.outputTab(outdict, outfile,  globs);
	# 				if globs['stats']:
	# 					line_start_time = RC.report_stats(globs, outdict['scaff'] + "-" + str(outdict['pos']), line_start_time);
	# 				del outdict;
	# 			pool.terminate();
	# 		if globs['stats']:
	# 			globs['pids'] = [globs['pids'][0]];
	# 		# The parallel version.
	# 	# Do the calculations on each input file.

#############################################################################
# THE REF CALC FUNCTION FOR THE LINE BY LINE PARALLELIZATION

# def refCalc(line_item):
# # Parses a line to get it ready to calculate a quality score and stores the output.
#     line, globs = line_item;
#     genotypes = ["AA", "AC", "AG", "AT", "CC", "CG", "CT", "GG", "GT", "TT"];

#     line = line.strip().split("\t");
#     scaff, pos, gl_list = line[0], int(line[1]), line[2:];

#     cor_ref, cor_score = "NA", "NA";

#     gls = { genotypes[x] : math.exp(float(gl_list[x])) for x in range(len(gl_list)) };
#     # Parse the info from the current line -- scaffold, position, genotype likelihoods.

#     if globs['fasta'] == 1:
#         ref = RC.fastaGet(globs['reffile'], globs['ref'][scaff])[1][pos-1];
#     elif globs['fasta'] == 2:
#         ref = globs['ref'][scaff][pos-1];
#     elif globs['fasta'] == 3:
#         ref = globs['ref'][scaff][pos-1];
#     # Gets the called reference base at the current position.

#     rq, lr, l_match, l_mismatch = calcScore(ref, gls);
#     # Call the scoring function.

#     if globs['correct-opt'] and rq in [0,-1,-3]:
#         cor_ref, cor_score = correctRef(rq, ref, gls);
#     # With --correct, suggest a better/corrected reference base if the score is negative (0), the reference is undetermined (-1), or no reads support the matching base (-3)

#     outdict = { 'scaff' : scaff, 'pos' : pos, 'ref' : ref, 'rq' : rq, 'lr' : lr,  
#                 'l_match' : l_match, 'l_mismatch' : l_mismatch, 'gls' : gls, 
#                 'cor_ref' : cor_ref, 'cor_score' : cor_score };
#     # Store the info from the current site to be written once returned.

#     return outdict;

#############################################################################
# OLD CODE WHEN TESTING MULTIPLE FASTA READERS

# parser.add_argument("-f", dest="fasta_opt", help=argparse.SUPPRESS, type=int, default=1);
# if args.fasta_opt in [1,2,3]:
# 	globs['fasta'] = args.fasta_opt;
# else:
# 	RC.errorOut(0, "Invalid fasta opt.", globs);
# FROM OPT PARSE

# if globs['fasta'] == 1:
# 	globs['ref'] = RC.fastaReadInd(globs['reffile']);
# # My fasta index functions
# elif globs['fasta'] == 2:
# 	globs['ref'] = RC.fastaRead(globs['reffile'], globs);
# # My fasta dict function
# elif globs['fasta'] == 3:
# 	from Bio import SeqIO
# 	globs['ref'] = SeqIO.to_dict(SeqIO.parse(globs['reffile'], "fasta"))
# # Index the reference FASTA file.
# FROM REFEREE

# if globs['fasta'] == 1:
# 	if last_scaff != scaff:
# 		seq = RC.fastaGet(globs['reffile'], globs['ref'][scaff])[1];
# 		last_scaff = scaff;
# 	ref = seq[pos-1].upper();
# elif globs['fasta'] == 2:
# 	ref = globs['ref'][scaff][pos-1].upper();
# elif globs['fasta'] == 3:
# 	ref = globs['ref'][scaff][pos-1].upper();
# # Gets the called reference base at the current position. 
# FROM REF CALC

# if globs['fasta'] == 1:
# 	seq = RC.fastaGet(globs['reffile'], globs['ref'][scaff])[1];
# elif globs['fasta'] == 2:
# 	seq = globs['ref'][scaff];
# elif globs['fasta'] == 3:
# 	seq = globs['ref'][scaff];
# FROM REF OUT

#############################################################################
# CHECK FOR BIOPYTHON

# try:
# 	from Bio import SeqIO
# except:
# 	sys.exit("\n*** ERROR: Your installation of Python is missing the Biopython module. Please install the module with: pip install biopython\n")
# First check if the argparse module is installed. If not, the input options cannot be parsed.

#############################################################################
# OLD FASTA DICTIONARY READER

# def fastaRead(i_name, globs):
# 	# This function reads a FASTA file into a dictionary.
# 	try:
# 		gzip_check = gzip.open(i_name).read(1);
# 		reader = gzip.open;
# 	except:
# 		reader = open;
# 	# Check if the reference file is gzipped, and if so set gzip as the file reader. Otherwise, read as a normal text file.

# 	seqdict = {};
# 	for line in reader(i_name):
# 		line = line.strip();
# 		if line[0] == '>':
# 			curkey = line[1:];
# 			seqdict[curkey] = "";
# 		else:
# 			seqdict[curkey] = seqdict[curkey] + line;

# 	if len(seqdict) == 0:
# 		errorOut(10, "Failed to read reference genome as FASTA file.", globs);
# 	else:
# 		return seqdict;

#############################################################################
# OLD EXAMPLE CALCS FOR SCORE TYPE 1 FOR CALCS.RMD

# First, we sum up the likelihoods of all genotypes that contain the reference allele ($L_{match}$) and separately sum up the likelihoods of all the genotypes that do not contain the reference allele ($L_{mismatch}$). 

# **Equation 4**

# $$ L_{match} = \sum_g^\mathbb{G} P(R\;|\;g) \; \text{if} \; B_R \in g $$

# **Equation 5**

# $$ L_{mismatch} = \sum_g^\mathbb{G} P(R\;|\;g) \; \text{if} \; B_R \notin g $$

# For instance, if our reference base was an A, then:

# $$ L_{match} = P(R|\{A,A\}) + P(R|\{A,T\}) + P(R|\{A,C\}) + P(R|\{A,G\})$$

# and:

# $$ L_{mismatch} = P(R|\{T,T\}) + P(R|\{T,C\}) + P(R|\{T,G\}) + P(R|\{C,C\}) + P(R|\{C,G\}) + P(R|\{G,G\})$$

# with the probabilities being calculated with Equation 1.

# We can then set up a likelihood ratio $LR$ by divding $L_{match}$ by $L_{mismatch}$:

# **Equation 6**

# $$ LR = \frac{L_{match}}{L_{mismatch}} $$

# And this can be log-scaled to get us an informative value for a quality score:

# **Equation 7**

# $$ Q_\mathbb{R} = \log{LR} $$

# ## III. Calculation of $Q_\mathbb{R}$ on example read sets

# **Example read sets:**

# ```{r read-sets, echo=FALSE}
# read_set = c("A","A","A","A","A","A","A","A","A","A","A","A","A","A","A","A","A","A","A","A")
# read_set_1a = list(num=1,reads=read_set,ref="A",ans="(correct)")
# read_set_1t = list(num=1,reads=read_set,ref="T",ans="(incorrect)")
# read_set_1c = list(num=1,reads=read_set,ref="C",ans="(incorrect)")
# read_set = c("A","A","A","A","A","A","A","A","A","A","A","A","A","A","A","A","A","A","A","T")
# read_set_2a = list(num=2,reads=read_set,ref="A",ans="(correct)")
# read_set_2t = list(num=2,reads=read_set,ref="T",ans="(incorrect)")
# read_set_2c = list(num=2,reads=read_set,ref="C",ans="(incorrect)")
# read_set = c("A","A","A","A","A","A","A","A","A","A","T","T","T","T","T","T","T","T","T","T")
# read_set_3a = list(num=3,reads=read_set,ref="A",ans="(correct)")
# read_set_3t = list(num=3,reads=read_set,ref="T",ans="(correct)")
# read_set_3c = list(num=3,reads=read_set,ref="C",ans="(incorrect)")

# rs1_df = data.frame(read_set=c("Reads","Base qual","Map qual"),
#                        reads=c("A  A  A  A  A  A  A  A  A  A  A  A  A  A  A  A  A  A  A  A",
#                                "40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 1-40",
#                                "40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 1-40"))

# rs1_table = kable(rs1_df, "html", caption="Read set 1") %>%
#   kable_styling(bootstrap_options=c("striped", "condensed", "responsive"), full_width=F)
# gsub("<thead>.*</thead>", "", rs1_table)

# rs2_df = data.frame(read_set=c("Reads","Base qual","Map qual"),
#                        reads=c("A  A  A  A  A  A  A  A  A  A  A  A  A  A  A  A  A  A  A  T",
#                                "40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 1-40",
#                                "40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 1-40"))

# rs2_table = kable(rs2_df, "html", caption="Read set 2") %>%
#   kable_styling(bootstrap_options=c("striped", "condensed", "responsive"), full_width=F)
# gsub("<thead>.*</thead>", "", rs2_table)

# rs3_df = data.frame(read_set=c("Reads","Base qual","Map qual"),
#                        reads=c("A  A  A  A  A  A  A  A  A  A  T  T  T  T  T  T  T  T  T  T",
#                                "40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 1-40",
#                                "40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 1-40"))

# rs3_table = kable(rs3_df, "html", caption="Read set 3") %>%
#   kable_styling(bootstrap_options=c("striped", "condensed", "responsive"), full_width=F)
# gsub("<thead>.*</thead>", "", rs3_table)
# ```

# The above read sets were plugged into the relevant equations to calculate $Q_\mathbb{R}$ with one read varying in both base and mapping quality. The countour plots show how each behave with different reference base calls. For example, with read set 1 (all As) and a reference base call of A we see high scores regardless of varying quality of a single read (upper left panel). However, the same read set when the reference base is called as a C scores very low, indicating that the reads do not support a C as the called base (lower left panel).

# **Examples of $Q_{ref}$**

# ```{r method2, fig.width=14, fig.height=11.2, fig.align="center", echo=FALSE, message=FALSE}
# method = 2
# read_set_1a_results = cycleReads(read_set_1a, method)
# rs1a_p = plotScores(read_set_1a_results, read_set_1a$num, read_set_1a$ref, read_set_1a$ans)
# read_set_1t_results = cycleReads(read_set_1t, method)
# rs1t_p = plotScores(read_set_1t_results, read_set_1t$num, read_set_1t$ref, read_set_1t$ans)
# read_set_1c_results = cycleReads(read_set_1c, method)
# rs1c_p = plotScores(read_set_1c_results, read_set_1c$num, read_set_1c$ref, read_set_1c$ans)
# read_set_2a_results = cycleReads(read_set_2a, method)
# rs2a_p = plotScores(read_set_2a_results, read_set_2a$num, read_set_2a$ref, read_set_2a$ans)
# read_set_2t_results = cycleReads(read_set_2t, method)
# rs2t_p = plotScores(read_set_2t_results, read_set_2t$num, read_set_2t$ref, read_set_2t$ans)
# read_set_2c_results = cycleReads(read_set_2c, method)
# rs2c_p = plotScores(read_set_2c_results, read_set_2c$num, read_set_2c$ref, read_set_2c$ans)
# read_set_3a_results = cycleReads(read_set_3a, method)
# rs3a_p = plotScores(read_set_3a_results, read_set_3a$num, read_set_3a$ref, read_set_3a$ans)
# read_set_3t_results = cycleReads(read_set_3t, method)
# rs3t_p = plotScores(read_set_3t_results, read_set_3t$num, read_set_3t$ref, read_set_3t$ans)
# read_set_3c_results = cycleReads(read_set_3c, method)
# rs3c_p = plotScores(read_set_3c_results, read_set_3c$num, read_set_3c$ref, read_set_3c$ans)

# method2 = grid.arrange(rs1a_p,rs2a_p,rs3a_p,rs1t_p,rs2t_p,rs3t_p,rs1c_p,rs2c_p,rs3c_p, ncol=3,nrow=3)

# result_list = list(read_set_1a_results, read_set_2a_results, read_set_3a_results,
#                     read_set_1t_results, read_set_2t_results, read_set_3t_results,
#                     read_set_1c_results, read_set_2c_results, read_set_3c_results)
# #topScores(result_list, 40)
# #topScores(result_list, 1)
# ```

# This has the desired behavior of being a high score when we are sure the reference base is correct and a low score when we are sure the reference base is not correct. In fact, it has the nice property of being centered around 0, with positive scores indicating support for the called reference base and negative scores indicating support for the reference base being an error. The closer to 0 the score is (positive or negative) the less confident we are in our assertion.

#############################################################################
# UNUSED OPTIONS

#parser.add_argument("-s", dest="startpos", help="Set the starting position for the input file(s). Default: 1", default=False);
#parser.add_argument("-e", dest="endpos", help="Set the end position for the input file(s). Default: last position in assembly/scaffold", default=False);
#parser.add_argument("-c", dest="score_cutoff", help="The cut-off score for --correct. Sites that score below this cut-off will have an alternate reference base suggested. If --correct isn't set, this option is ignored. Default: 1", default=False);
#parser.add_argument("--stats", dest="stats_opt", help=argparse.SUPPRESS, action="store_true", default=False);

#############################################################################
# SCORE METHOD 2 EXPLANATION

#  We also scale the genotype log-likelihoods by subtracting the largest likelihood from each score:

# **Equation 5**

# $$ P_{scaled}(R|\mathbb{G}) = P_{log}(R|\mathbb{G}) - \max{P_{log}(R|\mathbb{G})} $$


# Now we wish to compute a quality value $Q_{ref}$ for a reference base given a set of reads $R$ that map to that position. We want this number to represent the probability that the called base is an error such that it will be high when we are sure the reference base $B_R$ is correct and low when we are sure the reference base is incorrect.

# To do this, we simply sum up all of the likelihoods for genotypes that do not contain the reference base. First, we get out of the log scale:

# **Equation 6**

# $$ P(R|\mathbb{G}) = e^{P_{log}(R|\mathbb{G})} $$

# And then sum the appropriate likelihoods:

# **Equation 7**

# $$ L_{mismatch} = \sum_g^\mathbb{G} P(R\;|\;g) \; \text{if} \; B_R \notin g $$

# For instance, if our reference base was an A, then:

# $$ L_{mismatch} = P(R|\{T,T\}) + P(R|\{T,C\}) + P(R|\{T,G\}) + P(R|\{C,C\}) + P(R|\{C,G\}) + P(R|\{G,G\})$$

# Then we convert this to the Phred scale by taking the negative log to obatin a reference quality score, $Q_\mathbb{R}$:

# **Equation 8**

# $$ Q_\mathbb{R} = -\log{L_{mismatch}} $$

# We limit scores to a max of 90, with a few special cases (see [README](https://github.com/gwct/referee)). For fastq format, scores are translated as:

# **Equation 9**

# FASTQ score char = ascii(numerical score + 35)

# -----

# ## III. Calculation of $Q_\mathbb{R}$ on example read sets

# **Example read sets:**

# ```{r read-sets, echo=FALSE}
# read_set = c("A","A","A","A","A","A","A","A","A","A","A","A","A","A","A","A","A","A","A","A")
# read_set_1a = list(num=1,reads=read_set,ref="A",ans="(correct)")
# read_set_1t = list(num=1,reads=read_set,ref="T",ans="(incorrect)")
# read_set_1c = list(num=1,reads=read_set,ref="C",ans="(incorrect)")
# read_set = c("A","A","A","A","A","A","A","A","A","A","A","A","A","A","A","A","A","A","A","T")
# read_set_2a = list(num=2,reads=read_set,ref="A",ans="(correct)")
# read_set_2t = list(num=2,reads=read_set,ref="T",ans="(incorrect)")
# read_set_2c = list(num=2,reads=read_set,ref="C",ans="(incorrect)")
# read_set = c("A","A","A","A","A","A","A","A","A","A","T","T","T","T","T","T","T","T","T","T")
# read_set_3a = list(num=3,reads=read_set,ref="A",ans="(correct)")
# read_set_3t = list(num=3,reads=read_set,ref="T",ans="(correct)")
# read_set_3c = list(num=3,reads=read_set,ref="C",ans="(incorrect)")

# rs1_df = data.frame(read_set=c("Reads","Base qual","Map qual"),
#                        reads=c("A  A  A  A  A  A  A  A  A  A  A  A  A  A  A  A  A  A  A  A",
#                                "40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 1-40",
#                                "40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 1-40"))

# rs1_table = kable(rs1_df, "html", caption="Read set 1") %>%
#   kable_styling(bootstrap_options=c("striped", "condensed", "responsive"), full_width=F)
# gsub("<thead>.*</thead>", "", rs1_table)

# rs2_df = data.frame(read_set=c("Reads","Base qual","Map qual"),
#                        reads=c("A  A  A  A  A  A  A  A  A  A  A  A  A  A  A  A  A  A  A  T",
#                                "40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 1-40",
#                                "40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 1-40"))

# rs2_table = kable(rs2_df, "html", caption="Read set 2") %>%
#   kable_styling(bootstrap_options=c("striped", "condensed", "responsive"), full_width=F)
# gsub("<thead>.*</thead>", "", rs2_table)

# rs3_df = data.frame(read_set=c("Reads","Base qual","Map qual"),
#                        reads=c("A  A  A  A  A  A  A  A  A  A  T  T  T  T  T  T  T  T  T  T",
#                                "40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 1-40",
#                                "40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 1-40"))

# rs3_table = kable(rs3_df, "html", caption="Read set 3") %>%
#   kable_styling(bootstrap_options=c("striped", "condensed", "responsive"), full_width=F)
# gsub("<thead>.*</thead>", "", rs3_table)
# ```

# The above read sets were plugged into the relevant equations to calculate $Q_\mathbb{R}$ with one read varying in both base and mapping quality. The countour plots show how each behave with different reference base calls. 

# In the figure below, each panel represents the results of genotype likelihood calculations and reference quality score calculations on a combination of one reference base and one read set with single read varying in base (x-axis) and mapping quality (y-axis). The shading indicates the most likely genotype, while the labeled dashed lines indicate the reference quality scores.

# For example, in the upper left panel with read set 1 (all As) and a reference base call of A we see high scores regardless of varying quality of a single read. However, in the lower left panel the same read set when the reference base is called as a C scores very low, indicating that the reads do not support a C as the called base.

# **Examples of $Q_{ref}$**

# ```{r method2, fig.width=14, fig.height=11.2, fig.align="center", echo=FALSE, message=FALSE}
# method = 6
# read_set_1a_results = cycleReads(read_set_1a, method)
# rs1a_p = plotScores(read_set_1a_results, read_set_1a$num, read_set_1a$ref, read_set_1a$ans)
# read_set_1t_results = cycleReads(read_set_1t, method)
# rs1t_p = plotScores(read_set_1t_results, read_set_1t$num, read_set_1t$ref, read_set_1t$ans)
# read_set_1c_results = cycleReads(read_set_1c, method)
# rs1c_p = plotScores(read_set_1c_results, read_set_1c$num, read_set_1c$ref, read_set_1c$ans)
# read_set_2a_results = cycleReads(read_set_2a, method)
# rs2a_p = plotScores(read_set_2a_results, read_set_2a$num, read_set_2a$ref, read_set_2a$ans)
# read_set_2t_results = cycleReads(read_set_2t, method)
# rs2t_p = plotScores(read_set_2t_results, read_set_2t$num, read_set_2t$ref, read_set_2t$ans)
# read_set_2c_results = cycleReads(read_set_2c, method)
# rs2c_p = plotScores(read_set_2c_results, read_set_2c$num, read_set_2c$ref, read_set_2c$ans)
# read_set_3a_results = cycleReads(read_set_3a, method)
# rs3a_p = plotScores(read_set_3a_results, read_set_3a$num, read_set_3a$ref, read_set_3a$ans)
# read_set_3t_results = cycleReads(read_set_3t, method)
# rs3t_p = plotScores(read_set_3t_results, read_set_3t$num, read_set_3t$ref, read_set_3t$ans)
# read_set_3c_results = cycleReads(read_set_3c, method)
# rs3c_p = plotScores(read_set_3c_results, read_set_3c$num, read_set_3c$ref, read_set_3c$ans)

# method2 = grid.arrange(rs1a_p,rs2a_p,rs3a_p,rs1t_p,rs2t_p,rs3t_p,rs1c_p,rs2c_p,rs3c_p, ncol=3,nrow=3)

# result_list = list(read_set_1a_results, read_set_2a_results, read_set_3a_results,
#                     read_set_1t_results, read_set_2t_results, read_set_3t_results,
#                     read_set_1c_results, read_set_2c_results, read_set_3c_results)
# #topScores(result_list, 40)
# #topScores(result_list, 1)
# ```







		# with mp.Pool(processes=globs['num-procs']) as pool:
		# 	scaffs = [];
		# 	for scaff in globs['ref']:
		# 		scaffs.append(scaff);
		# 		if len(scaffs) == globs['num-procs']:
		# 			for result in pool.starmap(RC.getScaffLens, ((scaff, globs) for scaff in scaffs)):
		# 				#print(result);
		# 				globs['scaffs'][result[0]] = result[1];
		# 			scaffs = [];
		# This is slower for some reason