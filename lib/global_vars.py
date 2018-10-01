# This file holds some global variables for some of the input options.
# Global variables are exclusively read only.

import timeit, refcore as RC

def init():
    globs = {
        'starttime' : timeit.default_timer(),
        'startdatetime' : RC.getOutTime(),
        'start-pos' : 1,
        'end-pos' : False,
        'num-procs' : 1,
        'fastq' : False,
        'fastq-len' : 100,
        'correct-opt' : False,
        'correct-cutoff' : 1,
        'log-v' : 1,
        'mapped' : False,
        'stats' : False,
        'debug' : False,
        'scaff-lens' : {}
    }

    globs['logfilename'] = "referee-" + globs['startdatetime'] + ".log";
    globs['tmpdir'] = "referee.tmp." + globs['startdatetime'];

    return globs;