#!/usr/bin/python
############################################################
# For owl monkey, 12.17
# Using the output files from pileup_count_scaffold_base.py
# this script takes min and max read depth and counts the 
# number of sites.
# This is part of the error rate estimation.
############################################################

import sys, os, argparse, math, multiprocessing as mp

############################################################
# GLOBAL VARIABLES
parser = argparse.ArgumentParser(description="");
parser.add_argument("-s", dest="scaff_file", help="A file containing the list of scaffolds on which to run ANGSD.", default=False);
parser.add_argument("-r", dest="refdir", help="The path to the directory FASTA files for each scaffold. Scaffold IDs should match those in the scaffolds file (-s) exactly and be named [scaffold-id].fa", default=False);
parser.add_argument("-b", dest="bam_file", help="A BAM file with the reference genome's reads mapped back to the reference genome.", default=False);
parser.add_argument("-o", dest="outdir", help="Desired output directory location. Will create if not present.", default=False);
parser.add_argument("-p", dest="num_proc", help="The number of processes to use. Default = 1", type=int, default=1);
args = parser.parse_args();
# Input options.

# For owl monkey:
# -s /N/dc2/scratch/grthomas/qtip/owl-monkey/scaffolds-10kb.txt
# -r /N/dcwan/projects/hahnlab-phi/owl-monkey/ref-genome/genbank/scaffolds/
# -b /N/dcwan/projects/hahnlab-phi/owl-monkey/swapRef/owl-monkey-120ref-sorted.bam
# -o /N/dc2/scratch/grthomas/qtip/owl-monkey/angsd-out/

if any(a == False for a in [args.refdir, args.scaff_file, args.outdir]):
    print("\n ** Error: All input (-r, -s) and output (-o) options must be specified!\n");
    parser.print_help();
    sys.exit();
if not os.path.isdir(args.refdir):
    print("\n ** Error: Cannot find reference genome file (-r).\n");
    parser.print_help();
    sys.exit();
if not os.path.isfile(args.scaff_file):
    print("\n ** Error: Cannot find scaffolds file (-s).\n");
    parser.print_help();
    sys.exit();
if not os.path.isfile(args.bam_file):
    print("\n ** Error: Cannot find BAM file (-b).\n");
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
# Pertinant file and directory names.
############################################################
# FUNCTION DEFINITIONS
def runANGSD(scaff_item):
    scaffold, blank = scaff_item;
    scaff_ref = os.path.join(args.refdir, scaffold + ".fa");
    if not os.path.isfile(scaff_ref):
        return [False, "", "COULD NOT FIND SCAFF REF FILE", scaff];

    outfile = os.path.join(outdir, scaffold)
    angsd_cmd = "angsd -GL 2 -i " + args.bam_file + " -ref " + scaff_ref + " -minQ 0 -doGlf 4 -out " + outfile;

    try:
        print angsd_cmd;
    except:
        return [False, angsd_cmd, "FAILED ANGSD CMD", scaff];

    return [True, angsd_cmd, "", scaff];

############################################################
# MAIN BLOCK
if __name__ == '__main__':
    print;
    print " -> Run ANGSD";
    print " -> Call: " + " ".join(sys.argv);
    print " -> Output directory:", args.outdir;
    print;

    scaffs = { line : "" for line in open(args.scaff_file, "r").readlines() };
    # Read the scaffold IDs.

    with open(logfilename, "w") as logfile:
        logfile.write(" ".join(sys.argv) + "\n");
        num_scaffs = len(scaffs);
        counter = 1;
        if args.num_proc == 1:
            for scaff in scaffs.iteritems():
                result = runANGSD(scaff);
                if result[0]:
                    print counter, "/", num_scaffs, " -> ", result[3], " done!";
                else:
                    print counter, "/", num_scaffs, " -> ", result[3], " FAILED!";
                logfile.write(result[3] + " " + result[1] + " " + result[2] + "\n");
                counter += 1;
        # A serial version.
        else:
            pool = mp.Pool(processes = args.num_proc);
            for result in pool.imap_unordered(callHetAB, scaffs.iteritems()):
                result = runANGSD(scaff);
                if result[0]:
                    print counter, "/", num_scaffs, " -> ", result[3], " done!";
                else:
                    print counter, "/", num_scaffs, " -> ", result[3], " FAILED!";
                logfile.write(result[3] + " " + result[1] + " " + result[2] + "\n");
                counter += 1;
        # The parallel version

        print " -> Done!";
        print;

