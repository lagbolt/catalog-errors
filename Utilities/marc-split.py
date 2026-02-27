#
#   Read a MARC file and split each record into two parts, writing the first part to one output file
#   and the second part to another output file. The split happens on the first occurrence of a specified field.
#
#    Usage:  python marc-split.py
#               -i <MARC input file>
#               -o <MARC output file for records up to split>
#               -x <MARC output file for records at and after split> 
#               -f <field to split on>
#
#   For example:
#
#       python marc-split.py -i input.mrc -o output1.mrc -x output2.mrc -f 650
#
#   Assuming the splitting field occurs in every record, each output file will contain the same number of
#   records as the input file, but the fields in each input record will be split between the two output files.
#   The first output file will contain all fields up to (but not including) the first occurrence of a 650
#   field, and the second output file will contain the first 650 field and all subsequent fields.
#
#    If the splitting field does not occur in a record, that record will be written only to the first output
#    file and will not occur in the second output file.
#
#    If you find yourself wishing for something slightly different, please let me know.
#
#    Version:  0.1.0  2/26/26
#
#    License:  CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/
#
#    Graeme Williams
#    carryonwilliams@gmail.com
#

import argparse
from pymarc import MARCReader, MARCWriter, Record


class IncorrectOutputError(Exception):
    pass


def tags(record):
    return [f.tag for f in record.fields]


def process_input_file(args):
    split_field = args.field

    with (open(args.input, 'rb') as inf,
            open(args.output, 'wb') as outf,
            open(args.extra, 'wb') as extraf):
        reader = MARCReader(inf)
        writer = MARCWriter(outf)
        extrawriter = MARCWriter(extraf)
        
        for input_record in reader:

            if input_record is None: continue
            
            extra_flag = False
            extra_record = Record()
            original_tags = tags(input_record)  # needed for error check at end

            # all_fields is needed because  we are deleting fields from input_record
            all_fields = list(input_record.fields)
            for fld in all_fields:
                # Split on the first occurrence of the specified field and all subsequent fields
                if extra_flag or (fld.tag == split_field):
                    input_record.remove_field(fld)
                    extra_flag = True
                    extra_record.add_field(fld)

            writer.write(input_record)
            if extra_flag:
                extrawriter.write(extra_record)

            if original_tags != (tags(input_record) + tags(extra_record)):
                raise IncorrectOutputError("Output records do not match input record")      


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=("""Split each record in the input file into two records.
        Split happens on the first occurrence of the specified field.""")
        )   
    parser.add_argument("--input", "-i", required=True,
                        help="Input MARC file")
    parser.add_argument("--output", "-o", required=True,
                        help="Output MARC file for records up to split")
    parser.add_argument("--extra", "-x", required=True,
                        help="Output MARC file for records after split")
    parser.add_argument("--field", "-f", required=True,
                        help="Split input records on the first occurrence of this field")
    
    args = parser.parse_args()
    process_input_file(args)