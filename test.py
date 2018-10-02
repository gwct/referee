import sys, os, multiprocessing as mp

def testFunc(x):
    return x;

infilename = 'data/angsd-output-snippet-2.txt';
#f = open(infilename, "r");
#for line in f.iteritems():
#    print line;


if __name__ == '__main__':
    procs = 4;
    pool = mp.Pool(processes = procs);
    f = open(infilename, "r")
    for result in pool.map(testFunc, (line for line in f)):
        print result;