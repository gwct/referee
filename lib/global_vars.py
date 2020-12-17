# This file holds some global variables for some of the input options.
# Global variables are exclusively read only -- they are not modified anywhere else in the code except when reading the input options.

import timeit, sys, lib.refcore as RC

def init():
    globs = {
        'version' : '1.2',
        'releasedate' : 'August 08, 2020',
        'doi' : 'https://doi.org/10.1093/gbe/evz088',
        'http' : 'https://gwct.github.io/referee/',
        'github' : 'https://github.com/gwct/referee/issues',
        'starttime' : timeit.default_timer(),
        'startdatetime' : RC.getOutTime(),
        # Meta info

        'pyver' :  ".".join(map(str, sys.version_info[:3])),
        # System info

        'call' : "",
        # Script call info

        'in-file' : "",
        'in-type' : "",
        'ref-file' : "",
        'ref-index' : False,
        'num-procs' : 1,
        'lines-per-proc' : 100000,
        'chunk-size' : "NA",
        # Input locations

        'pileup-opt' : False,
        'haploid-opt' : False,
        'mapq-opt' : False,
        'reader' : open,
        "read-mode" : "r",
        'lread' : RC.readLine,
        # Input options

        'out-prefix' : "",
        'out-dir' : "",
        'out-tab' : "",
        'out-summary' : "",
        'out-fa' : "",
        'out-fq' : "",
        'bed-dir' : "",
        # Output locations

        'fastq-opt' : False,
        'fasta-opt' : False,
        
        'bed-opt' : False,
        'correct-opt' : False,
        'raw-opt' : False,
        'log-v' : 1,
        'mapped-only-opt' : False,
        'allcalc-opt' : False,
        # Output options

        'ref' : "",
        'scaff-lens' : {},
        'scaffs-written' : [],
        'num-scaffs' : "NA",
        'num-pos' : "NA",
        'genotypes' : ["AA", "AC", "AG", "AT", "CC", "CG", "CT", "GG", "GT", "TT"],
        'haploid-gt' : ["A","T","C","G"],
        
        'cur-fasta-seq' : "",
        'fasta-line-len' : 60,
        'scaff-errs' : 0,
        'scaff-unmapped' : 0,
        
        'cur-fastq-seq' : "",
        'cur-fastq-scores' : "",
        'cur-fastq-len' : 0,
        'fastq-line-len' : 100,
        # Seq info
        
        'bed-template' : {
            'out' : '', 'scaff' : '', 'scaff-start' : 0, 'scaff-len' : '', 
            'bins' : 
            {
                1 : { 'name' : '<=0', 'rgb' : "165,0,38", 'num-chunks' : 1, 'chunk-sizes' : ["0"], 'chunk-starts' : ["0"], 'last-pos' : 0, 'first-pos' : 0, 'shade' : 1000 },
                2 : { 'name' : '1-10', 'rgb' : "221,61,45", 'num-chunks' : 1, 'chunk-sizes' : ["0"], 'chunk-starts' : ["0"], 'last-pos' : 0, 'first-pos' : 0, 'shade' : 900  },
                3 : { 'name' : '11-20', 'rgb' : "246,126,75", 'num-chunks' : 1, 'chunk-sizes' : ["0"], 'chunk-starts' : ["0"], 'last-pos' : 0, 'first-pos' : 0, 'shade' : 800  },
                4 : { 'name' : '21-30', 'rgb' : "253,179,102", 'num-chunks' : 1, 'chunk-sizes' : ["0"], 'chunk-starts' : ["0"], 'last-pos' : 0, 'first-pos' : 0, 'shade' : 700  },
                5 : { 'name' : '31-40', 'rgb' : "254,218,139", 'num-chunks' : 1, 'chunk-sizes' : ["0"], 'chunk-starts' : ["0"], 'last-pos' : 0, 'first-pos' : 0, 'shade' : 600  },
                6 : { 'name' : '41-50', 'rgb' : "194,228,239", 'num-chunks' : 1, 'chunk-sizes' : ["0"], 'chunk-starts' : ["0"], 'last-pos' : 0, 'first-pos' : 0, 'shade' : 500  },
                7 : { 'name' : '51-60', 'rgb' : "152,202,225", 'num-chunks' : 1, 'chunk-sizes' : ["0"], 'chunk-starts' : ["0"], 'last-pos' : 0, 'first-pos' : 0, 'shade' : 400  },
                8 : { 'name' : '61-70', 'rgb' : "110,166,205", 'num-chunks' : 1, 'chunk-sizes' : ["0"], 'chunk-starts' : ["0"], 'last-pos' : 0, 'first-pos' : 0, 'shade' : 300  },
                9 : { 'name' : '71-80', 'rgb' : "74,123,183", 'num-chunks' : 1, 'chunk-sizes' : ["0"], 'chunk-starts' : ["0"], 'last-pos' : 0, 'first-pos' : 0, 'shade' : 200  },
                10 : { 'name' : '81+', 'rgb' : "54,75,154", 'num-chunks' : 1, 'chunk-sizes' : ["0"], 'chunk-starts' : ["0"], 'last-pos' : 0, 'first-pos' : 0, 'shade' : 100  }
            },
            'chunk-start' : 0, 'last-bin' : False, 'cur-bin' : ""
        },
        'cur-bed' : "",
        # Bed info
        # https://genome.ucsc.edu/FAQ/FAQformat.html#format1https://genome.ucsc.edu/FAQ/FAQformat.html#format1

        'endprog' : False,
        'quiet' : False,
        'progstarttime' : 0,
        'pids' : "",
        'method' : 1,
        'psutil' : "",
        'probs' : "",
        'debug' : False,
        'nolog' : False,
        'norun' : False,
        'exit-code' : 0,
        # Internal stuff

        'hist' : { 1 : {'min' : -3, 'max' : -3, 'count' : 0}, 
                    2 : {'min' : -2, 'max' : -2, 'count' : 0}, 
                    3 : {'min' : -1, 'max' : -1, 'count' : 0}, 
                    4 : {'min' : 0, 'max' : 0, 'count' : 0}, 
                    5 : {'min' : 1, 'max' : 10, 'count' : 0}, 
                    6 : { 'min' : 11, 'max' : 20, 'count' : 0}, 
                    7 : {'min' : 21, 'max' : 30, 'count' : 0}, 
                    8 : { 'min' : 31, 'max' : 40, 'count' : 0}, 
                    9 : {'min' : 41, 'max' : 50, 'count' : 0}, 
                    10 : {'min' : 51, 'max' : 60, 'count' : 0}, 
                    11 : {'min' : 61, 'max' : 70, 'count' : 0}, 
                    12 : {'min' : 71, 'max' : 80, 'count' : 0}, 
                    13 : {'min' : 81, 'max' : 90, 'count' : 0}, 
                    14 : {'min' : 91, 'max' : 91, 'count' : 0}, 
        },
        'num-corrected' : 0,

        'err-types' : { 'AT' : 0, 'AC' : 0, 'AG' : 0, 
                        'TA' : 0, 'TC' : 0, 'TG' : 0, 
                        'CT' : 0, 'CA' : 0, 'CG' : 0, 
                        'GT' : 0, 'GC' : 0, 'GA' : 0,
                        'NA' : 0, 'NT' : 0, 'NC' : 0, 'NG' : 0        
        }
    }

    globs['logfilename'] = "referee-" + globs['startdatetime'] + ".errlog";
    # Temporary logfile for errors that occur before the log file options are parsed.

    return globs;