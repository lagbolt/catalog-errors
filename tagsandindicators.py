#
#    Scan a MARC file and print out a count of each combination of tag, indicators
#    and $2 subfields.  It ignores 00X leader fields.
#
#    Usage:  python tag-summary.py  <MARC input file>
#
#    This is useful for getting an overview of the records in a MARC file and looking
#    for anomalies.
#
#    If you wan a hard copy of this output, you can copy the output into a multi-column
#    Word file and it will normally fit on one page.
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
from collections import Counter

summary = Counter()

with open(sys.argv[1], 'rb') as marc_input:
    for i, aRecord in enumerate(pymarc.MARCReader(marc_input)):
        for aField in aRecord.get_fields():
            if not aField.tag.startswith("00"):
                key = f"{aField.tag} {aField.indicator1} {aField.indicator2}"
                subfield2 = aField.get('2')       # defaults to None
                key = (key + ' $2' + subfield2) if subfield2 else key
                summary[key] += 1

for k, count in sorted(summary.items(), key=lambda item: item[0]):
    print(f"{count:3} {k}")
