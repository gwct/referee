import sys, os, multiprocessing as mp, lib.ref_calc as CALC, lib.ref_out as OUT



infilename = 'data/angsd-output-snippet.txt';
#f = open(infilename, "r");
#for line in f.iteritems():
#    print line;


if __name__ == '__main__':
    procs = 4;
    pool = mp.Pool(processes = procs);
    #f = open(infilename, "r")
    c = {1 : "A", 2 : "B", 3 : "C"}
    with open(infilename, "r") as infile:
        for outt in pool.map(CALC.testFunc, ((line, c) for line in infile)):
            print outt;
            OUT.testPrint(outt, c);
            #print result;   