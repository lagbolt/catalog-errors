#
#    Scan a MARC file or database table and count records that match specific tests
#    Check for possible duplicate author names
#
#    License:  CC BY 3.0 US, https://creativecommons.org/licenses/by/3.0/us/
#
#    Graeme Williams
#    carryonwilliams@gmail.com
#
#    Usage:  recordscan --inputfile <MARC input file>  [ --list <filename> ] [ --summary <filename> ]
#       or:  recordscan --inputtable <database table> [ --list <filename> ] [ --summary <filename> ]
#
#    The database table should have columns for bibnumber, tag, indicators, and tagData.
#    tagData is all the subfields glommed together.  You can get more information from
#    the mydb.py file.
#
#    There are two optional arguments to specify output files:  list and summary.  A list of problematic
#    6xx fields is written to the list file, with the limitation that a given subject heading is only
#    written out once.  A summary of problematic headings with a count is written to the summary file.
#
#    The default for either file is to write to the console / terminal where you're running the program.
#
# Known issues:  I really should check headings against the LC Name Authority File.
#

from collections import Counter
import re
import argparse
from pymarc import Record, Field
from typing import Callable, Set, List, Tuple  # just used for type hints

from lib import mymarc

# Globals!

recordCounter : Counter = Counter()
authorSet : Set[str] = set()

# Utility functions

def to_string_simple(the_Record : Record) -> str:
    # This is just for identifying faulty records in the output.
    # You can use whatever MARC fields you want here
    part1 = the_Record['001'].data if the_Record['001'] else "No 001"
    part2 = the_Record['245']['a'][:60] if the_Record['245'] else "No 245"
    return part1 + '/' + part2

# *** Next four functions are concerned with harvesting author data
# *** from the $a and $d subfields of 100 and 700 fields so we
# *** can check for possible duplicates (e.g., Smith, Bob ~ Smith, Bob, 1972-)

# for each 100 and 700 field the $a and $d fields are jammed together; we split them later
def collect_authors(arecord : Record):
    afield : Field = arecord['100']
    if afield and afield['a']:
        aname = afield['a'].rstrip(",.") + ("#" + afield['d'].rstrip(",.") if afield['d'] else "")
        authorSet.add(aname)
    for f in arecord.get_fields('700'):
        if f['a']:
            aname = f['a'].rstrip(",.") + ("#" + f['d'].rstrip(",.") if f['d'] else "")
            authorSet.add(aname)

    fieldlist = arecord['100'] if arecord['100'] else None
    fieldlist += arecord.get_fields('700')

# split author string into name, birth date, death date, with missing values == None
rgx = re.compile(r"(.*)(#\d{4}-)(\d{4}\.)?$")
def author_split(author_string : str) -> Tuple:
    m = rgx.match(author_string)
    if not m:
        return author_string, None, None
    return m[1], m[2], m[3] if m.lastindex == 3 else None

# When you're comparing two (name, birth date, death date) tuples, missing values match
# anything, so only two non-None values can produce a False result
def author_equals(x : str, y : str) -> bool:
    for ax, ay in zip(author_split(x.casefold()), author_split(y.casefold())):
        # ax and ay must be non-None to produce a false result
        if ax and ay and ax != ay:
            return False
    return True

# check for duplicate authors in global 'authorSet'
# authorSet is sorted so possible duplicate pairs are consecutive
def check_for_duplicate_authors() -> List[str]:
    result: List[str] = []
    prev = "+++++"
    for author in sorted(authorSet):
        if author_equals(author, prev):
            result.append(prev + " ~ " + author)
        prev = author
    return result

# *** Predicates that are too complicated to put into a lambda go here ***

def no1xx7xx(the_record : Record) -> bool:
    return not any([the_record[f] for f in ['100', '110', '700', '710','711', '720', '730']])

# return true if this record has a 245c with "and others" but no 1xx/7xx
# yes, I know this is an odd test; it was an experiment
def check245c1xx7xx(the_record : Record) -> bool:
    s = the_record['245']['c']
    return s and ("and others" in s) and no1xx7xx(theRecord)

# return true if this record has a 6xx field with indicator 2 = 7 but no $2 subfield
def indicator7butnodollar2(the_record : Record) -> bool:
    return any([f.indicator2=='7' and not f.get_subfields('2') for f in the_record.subjects()])

# Return true if this record has duplicate 650 subject headings,
# ignoring the trailing dot, if any.  The most common use case is
# to detect duplicates if you use both LCSH and FAST

def duplicate_subjects(the_record : Record) -> bool:
    # use only these fields in making the comparison
    subfields650 = ('a', 'b', 'c', 'd', 'v', 'x', 'y', 'z')
    field_list = []
    subject_fields = the_record.get_fields('650')
    if not subject_fields:
        return False
    # turn each 650 field into a dict and add it to field_list
    for f in subject_fields:
        field_dict = { k : f[k].rstrip('.') for k in subfields650 if f[k]}
        field_list.append(field_dict)
    # check the list for duplicate dicts
    for i in range(0, len(field_list)):
        if field_list[i] in field_list[i+1:]:
            return True
    return False

# turn a predicate into a function to check the record
# and count matching records, with optional print function

def checkfactory(label: str, predicate: Callable, print_this: Callable = None) -> Callable:

    # this function is returned by checkFactory, with bound values of label, predicate and print_this
    # note that 'label' is being used both as the Counter key and to label output
    def check(record):
        if predicate(record):
            recordCounter[label] += 1
            if print_this:
                print(label, ': ', print_this(record), sep='')

    recordCounter[label] = 0
    return check

# Construct list of checks from predicates.
# This list is a list of *functions*

checkList = (

    # using inline lambda functions
#    checkfactory('100', lambda r: r['100']),
    checkfactory('no 001', lambda r: not r['001']),
    checkfactory('no 006', lambda r : not r['006']),
    checkfactory('no 100', lambda r: not r['100']
                , to_string_simple
                ),
    checkfactory('245', lambda r: r['245']),
#    checkfactory('no 245', lambda r: not r['245']),
    checkfactory('no 245c', lambda r: not r['245']['c']
                , to_string_simple
                ),
    checkfactory('old style 041',
                 lambda r: r['041'] and r['041']['a'] and len(r['041']['a']) > 3
#                , lambda r : r['041']
                 ),
    checkfactory('041 but no 546', lambda r: r['041'] and not r['546']
                , to_string_simple 
                ),
    checkfactory('041h w. wrong indicator',
                 lambda r : r['041'] and r['041']['h'] and r['041'].indicators[0] != '1'
#                , lambda r : r['041']
                 ),
#    checkfactory('999', lambda r: r['999']),

    # using predicate functions defined above
    checkfactory('no 1xx or 7xx', no1xx7xx
                , to_string_simple
                ),
    checkfactory('"and others" in 245c but no 1xx/7xx', check245c1xx7xx),
    checkfactory('indicator 7 but no $2 in 6xx', indicator7butnodollar2
                , to_string_simple
                ),
    checkfactory('duplicate subject headings', duplicate_subjects
                , to_string_simple 
                )
)

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("--inputfile", "-if")
group.add_argument("--inputtable", "-it")

args = parser.parse_args()

# For each MARC record in the file or database table:
#   - collect authors from 100, 700;
#   - run each check in the checkList
for bibnum, theRecord in mymarc.recordgenerator(args.inputfile, args.inputtable):
    collect_authors(theRecord)
    for c in checkList:
        c(theRecord)

# print number of records found for each check.
# k is the label originally passed to checkfactory for each check
print("\nSummary of record found in different categories")
for k, n in recordCounter.items():
    print(n, "records have", k)

# print duplicate authors (e.g., Smith, Bob ~ Smith, Bob, 1972-)
print("\nPossible duplicate NARs")
print(*check_for_duplicate_authors(), sep="\n")

# print(sorted(authorSet))

