#!/usr/bin/python
############################################################
# For Referee, 10.18
# This takes a single bam file and splits it by scaffolds.
############################################################

import sys, os, argparse, math, multiprocessing as mp

############################################################
# GLOBAL VARIABLES
parser = argparse.ArgumentParser(description="");
parser.add_argument("-s", dest="scaff_file", help="A file containing the list of scaffolds to split up the BAM file by", default=False);
parser.add_argument("-b", dest="bam_file", help="A BAM file with the reference genome's reads mapped back to the reference genome.", default=False);
parser.add_argument("-o", dest="outdir", help="Desired output directory location. Will create if not present.", default=False);
parser.add_argument("-p", dest="num_proc", help="The number of processes to use. Default = 1", type=int, default=1);
args = parser.parse_args();
# Input options.

# For owl monkey:
# -s /N/dc2/scratch/grthomas/qtip/owl-monkey/scaffolds-list.txt
# -b /N/dcwan/projects/hahnlab-phi/owl-monkey/swapRef/owl-monkey-120ref-sorted.bam
# -o /N/dc2/scratch/grthomas/qtip/owl-monkey/split-bam-out/

if any(a == False for a in [args.scaff_file, args.bam_file, args.outdir]):
    print("\n ** Error: All input (-b, -s) and output (-o) options must be specified!\n");
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
logfilename = os.path.join(args.outdir, "split-bam.log");
#outfilename = os.path.join(args.outdir, "run-angsd-out.txt");
# Pertinant file and directory names.
############################################################
# FUNCTION DEFINITIONS
def samView(scaff_item):
    scaffold, blank = scaff_item;
    outfile = os.path.join(args.outdir, scaffold)
    samtools_cmd = "samtools view " + args.bam_file + " " + scaffold + " > " + outfile;
    try:
        #print samtools_cmd;
        os.system(samtools_cmd);
    except:
        return [False, samtools_cmd, "FAILED ANGSD CMD", scaffold];

    return [True, samtools_cmd, "", scaffold, outfile];

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

    with open(logfilename, "w") as logfile:
        logfile.write(" ".join(sys.argv) + "\n");
        num_scaffs = len(scaffs);
        counter = 1;
        if args.num_proc == 1:
            for scaff in scaffs.iteritems():
                result = samView(scaff);
                if result[0]:
                    print counter, "/", num_scaffs, " -> ", result[3], " done!";
                else:
                    print counter, "/", num_scaffs, " -> ", result[3], " FAILED!";
                logfile.write(result[3] + " " + result[1] + " " + result[2] + "\n");
                counter += 1;
        # A serial version.
        else:
            pool = mp.Pool(processes = args.num_proc);
            for result in pool.imap_unordered(samView, scaffs.iteritems()):
                if result[0]:
                    print counter, "/", num_scaffs, " -> ", result[3], " done!";
                else:
                    print counter, "/", num_scaffs, " -> ", result[3], " FAILED!";
                logfile.write(result[3] + " " + result[1] + " " + result[2] + "\n");
                counter += 1;
        # The parallel version

        print " -> Done!";
        print;
