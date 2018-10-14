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
        'stats' : False,
        'allcalc' : False,
        'pileup' : False,
        'progstarttime' : 0,
        'stepstarttime' : 0,
        'pids' : "",
        'reffile' : "",
        'ref' : "",
        'outdir' : "",
        'fasta' : 1
    }

    globs['logfilename'] = "referee-log-" + globs['startdatetime'] + ".log";
    globs['tmpdir'] = "referee-tmpdir-" + globs['startdatetime'] + "-" + RC.getRandStr();

    return globs;