import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--infile')
parser.add_argument('--outfile')
parser.add_argument('--prefixes')
parser.add_argument('--postfixes')
parser.add_argument('--partlist')

args = parser.parse_args()

print(args.infile)