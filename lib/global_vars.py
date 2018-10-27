# This file holds some global variables for some of the input options.
# Global variables are exclusively read only -- they are not modified anywhere else in the code.

import timeit, refcore as RC

def init():
    globs = {
        'starttime' : timeit.default_timer(),
        'startdatetime' : RC.getOutTime(),
        'start-pos' : False,
        'end-pos' : False,
        'num-procs' : 1,
        'fastq' : False,
        'fastq-len' : 100,
        'correct-opt' : False,
        #'correct-cutoff' : 1,
        'log-v' : 1,
        'mapped' : False,
        'stats' : True,
        'allcalc' : False,
        'pileup' : False,
        'mapq' : False,
        'progstarttime' : 0,
        'stepstarttime' : 0,
        'pids' : "",
        'reffile' : "",
        'ref' : "",
        'outdir' : "",
        'fasta' : 1,
        'method' : 1,
        'genotypes' : ["AA", "AC", "AG", "AT", "CC", "CG", "CT", "GG", "GT", "TT"],
        'psutil' : "",
        'probs' : "",
        'debug' : False
    }

    globs['logfilename'] = "referee-log-" + globs['startdatetime'] + ".log";
    globs['tmpdir'] = "referee-tmpdir-" + globs['startdatetime'] + "-" + RC.getRandStr();

    return globs;