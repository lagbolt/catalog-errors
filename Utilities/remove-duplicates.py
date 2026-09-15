#
#    Read records from a MARC file and remove duplicate fields based on 
#    string normalization of alphabetic subfields.  See the code below
#    for details of the normalization.
#
#    Usage:  python remove-duplicates.py
#                -i <input MARC file>
#                -o <output MARC file>
#                [ -f <field tag> ]
#                [ -d ]
#
#    Normalization rules for duplication check:
#    (i)   Extract and concatenate all alphabetic subfields.
#    (ii)  Remove everything but letters.
#    (iii) Convert to lowercase.
#
#    The -f / --field option defaults to 650.
#    The -d / --debug option prints record numbers and deleted fields.
#
#    A summary of records processed, records changed, and fields deleted 
#    is displayed at the end.
#
#    Version:  0.1.0  3/2/26
#
#    License:  CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/
#
#    Graeme Williams
#    carryonwilliams@gmail.com
#

import sys
import argparse
import re
from pymarc import MARCReader, MARCWriter

def normalize_field(field):
    """
    Normalizes a MARC field according to the following rules:
    (i)   Extract and concatenate all alphabetic subfields, but not numeric subfields
    (ii)  Remove everything but letters
    (iii) Convert to lowercase
    """
    # (i) Extract and concatenate all alphabetic subfields (a-z, A-Z)
    extracted_parts = [subfield.value for subfield in field.subfields if subfield.code.isalpha()]
    concatenated = "".join(extracted_parts)
    
    # (ii) Remove everything but letters
    letters_only = re.sub(r'[^a-zA-Z]', '', concatenated)
    
    # (iii) Convert to lowercase
    return letters_only.lower()

def process_marc(input_file, output_file, target_field, debug=False):
    """
    Reads records from input_file, removes duplicate fields (specified by target_field),
    and writes to output_file. Tracks and prints record and field counts.
    If debug is True, prints details of modified records.
    """
    records_processed = 0
    records_changed = 0
    fields_deleted = 0

    with open(input_file, 'rb') as inf:
        reader = MARCReader(inf)
        with open(output_file, 'wb') as outf:
            writer = MARCWriter(outf)
            
            for record in reader:
                if record is None:
                    continue
                
                records_processed += 1
                
                # Track fields for the current record in normalized form
                seen_normalized = set()
                to_be_deleted = []
                
                for field in record.fields:
                    if field.tag == target_field:
                        norm = normalize_field(field)
                        if norm in seen_normalized:
                            to_be_deleted.append(field)
                        else:
                            seen_normalized.add(norm)
                
                # Remove the duplicate fields
                if to_be_deleted:
                    records_changed += 1
                    fields_deleted += len(to_be_deleted)
                    
                    if debug:
                        print(f"Record {records_processed}:")
                        for field in to_be_deleted:
                            print(f"  Deleting duplicate field: {field}")
                    
                    for field in to_be_deleted:
                        record.remove_field(field)
                
                # Write the record to the output file
                writer.write(record)
            
            writer.close()

    print(f"Summary:")
    print(f"  Records processed: {records_processed}")
    print(f"  Records changed:   {records_changed}")
    print(f"  Fields deleted:    {fields_deleted}")

def main():
    parser = argparse.ArgumentParser(description="Remove duplicate fields from MARC records.")
    parser.add_argument("-i", "--input", required=True, help="Input MARC file path")
    parser.add_argument("-o", "--output", required=True, help="Output MARC file path")
    parser.add_argument("-f", "--field", default="650", help="MARC field tag to deduplicate (default: 650)")
    parser.add_argument("-d", "--debug", action="store_true", help="Print record number and deleted fields for modified records")
    
    args = parser.parse_args()
    
    process_marc(args.input, args.output, args.field, args.debug)

if __name__ == "__main__":
    main()
