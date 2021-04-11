#
#    Scan a MARC file or database table and check subject headings in 6xx fields
#    against subject terms extracted from an LCSH file downloaded from the Library of Congress.
#
#    Usage:  python sh-check.py --inputfile <MARC input file>  [ --list <filename> ] [ --summary <filename> ]
#       or:  python sh-check.py --inputtable <database table> [ --list <filename> ] [ --summary <filename> ]
#
#    The database table should have columns for bibnumber, tag, indicators, and tagData.
#    tagData is all the subfields glommed together.  You can get more information from
#    the mydb.py file.
#
#    The --list argument specifies a file for a listing of the first occurrence of each 'bad' (= unrecognized)
#    heading.  The default is to write the listing to the terminal.  If you want the listing to include *every*
#    occurrence, edit the code below to remove 'errorSet'
#
#    The -summary argument specifies a file for a summary giving each 'bad' (= unrecognized) heading and a
#    count.  The default is to write the summary to the terminal
#
#    Known issues:
#
#    I should check headings against the Library of Congress Name Authority File.
#
#    The way I process the downloaded subject headings loses the distinction between $a terms and
#    $x, $y and $z subdivisions.
#
#    Version:  0.1.0  1/1/21
#
#    License:  CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/
#
#    Graeme Williams
#    carryonwilliams@gmail.com
# 

from collections import Counter
import argparse
import contextlib
import sys

from lib import mymarc

#######

# Read MARC from database or file and pull out LC subject fields

########

def subjectheadinggenerator(recordgenerator):
    # therecord is a pymarc Record
    for bibnumber, therecord in recordgenerator:
        # if you're reading from a MARC file, bibnumber
        # will be empty.  You can set it from therecord here
        for subjectfield in therecord.subjects():
            if subjectfield.indicator2 == "0":       # this is the only case we're handling
                yield bibnumber, subjectfield

#######

# wrapper so stdout looks like a file with a context manager

#######

def create_file_context(file, mode="", encoding="utf-8"):
    if isinstance(file, str):
        # If string, open file
        return open(file, mode=mode, encoding=encoding)
    else:
        # Caller is responsible for closing file
        return contextlib.nullcontext(file)


#########

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--inputfile", "-if")
    group.add_argument("--inputtable", "-it")
    parser.add_argument("--list", "-l")
    parser.add_argument("--summary", "-s")
    args = parser.parse_args()

    recordgenerator = mymarc.recordgenerator(args.inputfile, args.inputtable)

    listfile = args.list if args.list else sys.stdout
    summaryfile = args.summary if args.summary else sys.stdout

    # Load phrase list for LC subject headings

    subjectTermsSet = set()
    with open("lcsh-subject-terms.txt", encoding="utf-8") as phraseFile:
        for phrase in phraseFile:
            subjectTermsSet.add(phrase.rstrip())

    # Load entries from LC children's headings and pull out phrases

    childrenstermsSet = set()
    with open("lcsj-entries.txt", encoding="utf-8") as childrensFile:
        for entry in childrensFile:
            for phrase in entry.strip().split("--"):
                childrenstermsSet.add(phrase)

    # Now that we have the LC data loaded, scan the input file / table

    errorCounter = Counter()
    errorSet = set()             # just so we don't print a given bad heading twice

    with create_file_context(listfile, 'w', encoding="utf-8") as outfile:
        for c, (bn, thefield) in enumerate(subjectheadinggenerator(recordgenerator)):

            # limiting c to a low value is just a cheap way to limit the damage while debugging
            if c > 999999:
                break

            printString = f"{bn} : {thefield.tag} {str(thefield.indicators)} : "
            printFlag = False
            for subfieldcode, subfieldvalue in thefield:
                subfieldvalue =  mymarc.namestrip(subfieldvalue)  # strip punctuation
                printString += "$" + subfieldcode + ":" + subfieldvalue
                if "Fictitious character" in subfieldvalue:
                    printString += "(FC) : "
                    printFlag = False        # forgive earlier errors
                elif subfieldcode == 'd':    # date => person from LCNAF
                    printString += "(D) : "     # D for date
                    printFlag = False        # forgive earlier errors (presumably name)
                elif subfieldcode in ['c', 'v', '2']:
                    printString += "(I) : "     # I for ignore
                elif subfieldvalue in subjectTermsSet:
                    printString += "(Y) : "  # Y for yes, found
                elif subfieldvalue in childrenstermsSet:
                    printString += "(C) : "     # C for children's subject heading
                    # this is an error because the second indicator = 1
                    printFlag = printFlag if subfieldvalue in errorSet else True
                    errorSet.add(subfieldvalue)
                    errorCounter[subfieldvalue+"(C)"] += 1
                else:
                    printString += "(N) : "
                    printFlag = printFlag if subfieldvalue in errorSet else True
                    errorSet.add(subfieldvalue)
                    errorCounter[subfieldvalue+"(N)"] += 1

            if printFlag:
                print(printString, file=outfile)

    with create_file_context(summaryfile, 'w', encoding="utf-8") as outfile:
        for k, v in errorCounter.items():
            print(f"{v}, {k}", file=outfile)

if __name__ == "__main__":
    main()