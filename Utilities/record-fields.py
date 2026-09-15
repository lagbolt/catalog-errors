#
#    Scan a MARC file and print out (as text) particular fields from each record.
#
#    Usage:  python record-fields.py  
#               -if <MARC input file>
#               [ -of <output file> ]
#               [ -sep <record separator string> ]
#               -t tag-match-1 tag-match-2 ...
#
#    The output file defaults to the console.
#
#    For each record in the input file, prints out the fields that match any tag-match argument.
#
#    The tag-match arguments can be 1, 2 or 3 characters long.  For example, '1' matches any 1XX field,
#    65 matches any 65X field, and 245 matches only the 245 field.
#
#
#    Version:  0.2.2  2/25/26
#
#    License:  CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/
#
#    Graeme Williams
#    carryonwilliams@gmail.com
#

import argparse
import contextlib
import pymarc
import sys

# wrapper so stdout looks like a file with a context manager

def create_file_context(file, mode="", encoding="utf-8"):
    if isinstance(file, str):
        # If string, open file
        return open(file, mode=mode, encoding=encoding)
    else:
        # Caller is responsible for closing file
        return contextlib.nullcontext(file)

parser = argparse.ArgumentParser()
parser.add_argument("--inputfile", "-if", help="MARC file to read", required=True)
parser.add_argument("--outputfile", "-of", help="output file", required=False, default=sys.stdout)
parser.add_argument("--separator", "-sep", help="separator between records", required=False, default=None)
parser.add_argument("--tags", "-t", help="output fields with these tags", required=True, nargs="+")
args = parser.parse_args()

tag_matches = tuple(args.tags)
record_separator = args.separator

with ( open(args.inputfile, 'rb') as marc_input,
        create_file_context(args.outputfile, mode="w", encoding="utf-8") as output_file):
    for i, aRecord in enumerate(pymarc.MARCReader(marc_input)):
        printFlag = False      # did I print any fields from this record?
        for aField in aRecord.fields:
            if aField.tag.startswith(tag_matches):
                printFlag = True
                try:
                    print(f"{i:4}:  {aField}", file=output_file)
                except UnicodeEncodeError:
                    print(f"{i:4}:  {aField.tag}  ENCODING ERROR", file=output_file)
        if printFlag and record_separator:
            print(record_separator, file=output_file)