import sys, os, argparse

print()
print("###### Build site pages ######");
print("PYTHON VERSION: " + ".".join(map(str, sys.version_info[:3])))
print("# Script call: " + " ".join(sys.argv) + "\n----------");

parser = argparse.ArgumentParser(description="Gets stats from a bunch of abyss assemblies.");
parser.add_argument("--all", dest="all", help="Build all pages", action="store_true", default=False);
parser.add_argument("--index", dest="index", help="Without --all: build index.html. With --all: exlude index.html", action="store_true", default=False);
parser.add_argument("--calcs", dest="calcs", help="Without --all: build calcs.html. With --all: exlude calcs.html", action="store_true", default=False);
parser.add_argument("--scores", dest="scores", help="Without --all: build scores.html. With --all: exlude scores.html", action="store_true", default=False);
parser.add_argument("--readme", dest="readme", help="Without --all: build readme.html. With --all: exlude readme.html", action="store_true", default=False);
parser.add_argument("--walkthrough", dest="walkthrough", help="Without --all: build walkthrough.html. With --all: exlude walkthrough.html", action="store_true", default=False);
parser.add_argument("--links", dest="links", help="Without --all: build links.html. With --all: exlude links.html", action="store_true", default=False);
args = parser.parse_args();
# Input options.

#cwd = os.getcwd();
os.chdir("generators");

pages = {
    'index' : args.index,
    'calcs' : args.calcs,
    'scores' : args.scores,
    'readme' : args.readme,
    'walkthrough' : args.walkthrough,
    'links' : args.links,
}

if args.all:
    pages = { page : False if pages[page] == True else True for page in pages };

if pages['index']:
    os.system("python index_generator.py");

if pages['calcs']:
    os.system("python calcs_generator.py");

if pages['scores']:
    os.system("python scores_generator.py");

if pages['readme']:
    os.system("python readme_generator.py");

if pages['links']:
    os.system("python links_generator.py");

print("----------\nDone!");


