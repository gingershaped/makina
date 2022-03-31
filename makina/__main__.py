import argparse
import makina
from makina.displays import *

parser = argparse.ArgumentParser(description = "Run Makina programs")
parser.add_argument('file', metavar='file', help='A path to the file to run')
parser.add_argument('--fancy', action='store_true', help="Enable the fancy display (slows program considerably)")
args = parser.parse_args()
makina.run(open(args.file, "r").read(), display = FancyDisplay if args.fancy else None)