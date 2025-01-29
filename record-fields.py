#
#    Scan a MARC file and print out particular fields from each record.
#
#    Usage:  python record-fields.py  <MARC input file>  tag-match-1 tag-match-2 ...
#
#    For each record in the input file, prints out the fields that match any tag-match argument.
#
#    The tag-match arguments can be 1, 2 or 3 characters long.  For example, '1' matches any 1XX field,
#    65 matches any 65X field, and 245 matches only the 245 field.
#
#
#    Version:  0.1.0  1/26/25
#
#    License:  CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/
#
#    Graeme Williams
#    carryonwilliams@gmail.com
#

import pymarc
import sys

tag_matches = sys.argv[2:]

def match_tag(tag):
    return any (
        ( tag[:len(m)]==m for m in tag_matches )
    )

with open(sys.argv[1], 'rb') as marc_input:
    for i, aRecord in enumerate(pymarc.MARCReader(marc_input)):
        for aField in aRecord.get_fields():
            if match_tag(aField.tag):
                try:
                    print(f"{i:2}:  {aField}")
                except UnicodeEncodeError:
                    print(f"{i:2}:  {aField.tag}  ENCODING ERROR")
        print(10*"  -")
 