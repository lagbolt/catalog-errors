import pymarc
import sys

acc = dict()

if len(sys.argv) < 2:
    print("Please specify an input file on the command line")
else:
    with open(sys.argv[1], 'rb') as marc_input:
        for theRecord in pymarc.MARCReader(marc_input):
            for theField in theRecord.get_fields():
                tag = theField.tag
                indicators = "  " if tag.startswith("00") else theField.indicator1 + theField.indicator2
                key = tag + '-' + indicators
                acc[key] = acc.get(key, 0) + 1
    for key in sorted(acc):
        print(key, acc[key])