#
#    Read records from a MARC file and, using the author and title information, gets series information from Goodreads.
#    The series information from Goodreads, if any, is compared to the series information in the records 490, 800 and
#    and 830 fields, if any.
#
#    Usage:  python goodreads-seriescheck.py -if <MARC input file> [ -of <output file> ] [ -sep <separator> ]
#
#    The output file is written in Excel-compatible CSV file.  The output file defaults to the console.
#    The separator defaults to comma.
#
#    The columns in the CSV file are:  an index number, the 100a, the 245a, the 490a or None, the 800t or 830a or None,
#    the series information from Goodreads, and a 'Y' indication if the series information from Goodreads does not
#    matches the series information in the record.
#
#    If you find yourself wishing for a different format.
#
#    Version:  0.2.0  2/8/25
#
#    License:  CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/
#
#    Graeme Williams
#    carryonwilliams@gmail.com
#



import argparse
import contextlib
import csv
import pymarc
import requests
import sys

from lib import goodreads

def get_subfield(theRecord, tag, subfield):
    if not (fld := theRecord.get(tag)):
        return "None"
    if subfield := fld.get(subfield):
        return subfield
    else:
        return "None"
    
def get_series(theRecord):
    if (fld := theRecord.get("800")):
        return fld.get("t") or "None"
    elif (fld := theRecord.get("830")):
        return fld.get("a") or "None"
    else:
        return "None"
    
def compare_series(series_490, series_800, gr_series):
    if not gr_series:
        return "None"
    return (gr_series == series_490) or (gr_series == series_800)

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
parser.add_argument("--outputfile", "-of", help="CSV output file", required=False, default=sys.stdout)
parser.add_argument("--separator", "-sep", help="CSV separator character(s)", required=False, default=",")
args = parser.parse_args()

with requests.Session() as session:
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'})
   # Iterate over the records in the file and call Goodreads to get the series
    with ( open(args.inputfile, 'rb') as marc_input,
          create_file_context(args.outputfile, mode="w", encoding="utf-8") as csv_output):
        writer = csv.writer(csv_output, delimiter=args.separator)
        writer.writerow(["Index", "100a", "245a", "490a", "800t/830a", "Goodreads series", "Mismatch?"])
        for i, aRecord in enumerate(pymarc.MARCReader(marc_input)):
            author = get_subfield(aRecord, "100", "a").strip(",")
            title = get_subfield(aRecord, "245", "a").strip(" /:")
            series_490 = get_subfield(aRecord, "490", "a").strip(" ;")
            series_8XX = get_series(aRecord).strip(" ;")

            # get data from Goodreads corresponding to the record
            worknumber = goodreads.get_worknumber(session, author.split(',')[0], title)
            if not worknumber:
                gr_series = "No title match"
                indicator = " "
            else:
                gr_series = goodreads.get_seriesname(session, worknumber)
                indicator = " " if compare_series(series_490, series_8XX, gr_series) else "Y"
            writer.writerow([i, author, title, series_490, series_8XX, gr_series, indicator])