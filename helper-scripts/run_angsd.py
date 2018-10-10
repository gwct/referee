#!/usr/bin/python
############################################################
# For Referee, 10.18
# This takes a set of bam files and a reference genome and
# uses ANGSD to calculate genotype likelihoods on each bam
# file.
############################################################

import sys, os, argparse, math, multiprocessing as mp

############################################################
# GLOBAL VARIABLES
parser = argparse.ArgumentParser(description="");
parser.add_argument("-s", dest="scaff_file", help="A file containing the list of scaffolds on which to run ANGSD.", default=False);
parser.add_argument("-r", dest="refdir", help="The path to the directory containing reference genome FASTA files split by scaffold. Scaffold IDs should match those in the scaffolds file (-s) exactly", default=False);
parser.add_argument("-b", dest="bamdir", help="The path to a directory containing a BAM file for each scaffold with the reference genome's reads mapped back to the reference genome.", default=False);
parser.add_argument("-o", dest="outdir", help="Desired output directory location. Will create if not present.", default=False);
parser.add_argument("-p", dest="num_proc", help="The number of processes to use. Default = 1", type=int, default=1);
args = parser.parse_args();
# Input options.

# For owl monkey:
# -s /N/dc2/scratch/grthomas/qtip/owl-monkey/scaffolds-list.txt
# -r /N/dcwan/projects/hahnlab-phi/owl-monkey/ref-genome/genbank/GCA_000952055.2_Anan_2.0_genomic.fna
# -b /N/dc2/scratch/grthomas/qtip/owl-monkey/split-bam-out/
# -o /N/dc2/scratch/grthomas/qtip/owl-monkey/angsd-out/

if any(a == False for a in [args.refdir, args.scaff_file, args.bamdir, args.outdir]):
    print("\n ** Error: All input (-r, -s, -b) and output (-o) options must be specified!\n");
    parser.print_help();
    sys.exit();
if not os.path.isdir(args.refdir):
    print("\n ** Error: Cannot find reference genome directory (-r).\n");
    parser.print_help();
    sys.exit();
if not os.path.isfile(args.scaff_file):
    print("\n ** Error: Cannot find scaffolds file (-s).\n");
    parser.print_help();
    sys.exit();
if not os.path.isdir(args.bamdir):
    print("\n ** Error: Cannot find BAM directory (-b).\n");
    parser.print_help();
    sys.exit();
if args.num_proc < 1:
    print("\n ** Error: The number of processes specified with -p must be greater than 0!\n");
    parser.print_help();
    sys.exit();

if not os.path.isdir(args.outdir):
    print(" ++ Making output directory: " + args.outdir);
    os.makedirs(args.outdir);
logfilename = os.path.join(args.outdir, "run-angsd.log");
outfilename = os.path.join(args.outdir, "run-angsd-out.txt");
# Pertinant file and directory names.
############################################################
# FUNCTION DEFINITIONS
def runANGSD(scaff_item):
    scaffold, blank = scaff_item;
    scaff_ref = os.path.join(args.refdir, scaffold + ".fa");
    if not os.path.isfile(scaff_ref):
        return [False, "", "COULD NOT FIND SCAFF REF FILE", scaffold];
    scaff_bam = os.path.join(args.bamdir, scaffold + ".bam");
    if not os.path.isfile(scaff_bam):
        return [False, "", "COULD NOT FIND SCAFF BAM FILE", scaffold];

    outfile = os.path.join(args.outdir, scaffold)
    angsd_cmd = "angsd -GL 2 -i " + scaff_bam + " -ref " + scaff_ref + " -minQ 0 -doGlf 4 -out " + outfile;

    try:
        print angsd_cmd;
    except:
        return [False, angsd_cmd, "FAILED ANGSD CMD", scaffold];

    return [True, angsd_cmd, "", scaffold, outfile];

############################################################
# MAIN BLOCK
if __name__ == '__main__':
    print;
    print " -> Run ANGSD";
    print " -> Call: " + " ".join(sys.argv);
    print " -> Output directory:", args.outdir;
    print;

    scaffs = { line.strip() : "" for line in open(args.scaff_file, "r").readlines() };
    # Read the scaffold IDs.

    with open(logfilename, "w") as logfile, open(outfilename, "w") as mainoutfile:
        logfile.write(" ".join(sys.argv) + "\n");
        num_scaffs = len(scaffs);
        counter = 1;
        if args.num_proc == 1:
            for scaff in scaffs.iteritems():
                result = runANGSD(scaff);
                if result[0]:
                    print counter, "/", num_scaffs, " -> ", result[3], " done!";
                    mainoutfile.write(result[4] + "\n");
                else:
                    print counter, "/", num_scaffs, " -> ", result[3], " FAILED!";
                logfile.write(result[3] + " " + result[1] + " " + result[2] + "\n");
                counter += 1;
        # A serial version.
        else:
            pool = mp.Pool(processes = args.num_proc);
            for result in pool.imap_unordered(runANGSD, scaffs.iteritems()):
                result = runANGSD(scaff);
                if result[0]:
                    print counter, "/", num_scaffs, " -> ", result[3], " done!";
                    mainoutfile.write(result[4] + "\n");
                else:
                    print counter, "/", num_scaffs, " -> ", result[3], " FAILED!";
                logfile.write(result[3] + " " + result[1] + " " + result[2] + "\n");
                counter += 1;
        # The parallel version

        print " -> Done!";
        print;

