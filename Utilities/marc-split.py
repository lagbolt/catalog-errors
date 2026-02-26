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