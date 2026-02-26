import sys
import re
import argparse
from pymarc import MARCReader, MARCWriter

def check_match(record, tag, subfield_code, pattern):
    """Checks if a single tag/subfield in a record matches a regex pattern."""
    target_fields = record.get_fields(tag)
    for field in target_fields:
        if subfield_code:
            sub_values = field.get_subfields(subfield_code)
            if any(pattern.search(val) for val in sub_values):
                return True
        else:
            if pattern.search(field.value()):
                return True
    return False

def process_marc(args):
    # Setup filter logic if a match expression is provided
    filters = []
    eval_logic = "True" # Default to matching everything if no expression
    
    if args.match:
        filter_regex = r'(\d{3})\s+(?:\$([a-z0-9])\s+)?("(?:[^"\\]|\\.)*"|\S+)'
        
        def filter_replacer(match):
            tag = match.group(1)
            subfield = match.group(2) 
            pattern_raw = match.group(3).strip('"') 
            try:
                compiled_re = re.compile(pattern_raw, re.IGNORECASE)
                filters.append((tag, subfield, compiled_re))
                return f"__results[{len(filters)-1}]"
            except re.error:
                print(f"Invalid regex in expression: {pattern_raw}")
                sys.exit(1)

        eval_logic = re.sub(filter_regex, filter_replacer, args.match)
        eval_logic = eval_logic.replace("AND", " and ").replace("OR", " or ").replace("NOT", " not ")

    match_count = 0
    total_records = 0

    try:
        with open(args.input, 'rb') as inf:
            reader = MARCReader(inf)
            writer = MARCWriter(open(args.output, 'wb')) if args.output else None
            
            for record in reader:
                if record is None: continue
                total_records += 1
                
                # Evaluate filters for this record
                results = [check_match(record, t, s, p) for t, s, p in filters]
                
                if eval(eval_logic, {"__builtins__": {}}, {"__results": results}):
                    match_count += 1
                    
                    # Handle output to file
                    if writer:
                        if args.fields:
                            # Create a shell record with only requested fields for file output
                            from pymarc import Record
                            new_rec = Record()
                            new_rec.leader = record.leader
                            for tag in args.fields:
                                for field in record.get_fields(tag):
                                    new_rec.add_field(field)
                            writer.write(new_rec)
                        else:
                            writer.write(record)
                    
                    # Handle output to terminal (if no output file specified)
                    else:
                        print(f"--- Record {match_count} ---")
                        display_tags = args.fields if args.fields else [f.tag for f in record.fields]
                        for tag in display_tags:
                            for field in record.get_fields(tag):
                                print(f"{tag}: {field.value()}")
            
            if writer:
                writer.close()
        
        if args.count:
            print(f"\nProcessed {total_records} records. Found {match_count} matches.")

    except Exception as e:
        print(f"Error during processing: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter and display MARC records.")
    parser.add_argument("--input", "-i", required=True, help="Input MARC file")
    parser.add_argument("--output", "-o", help="Output MARC file (writes to terminal if omitted)")
    parser.add_argument("--match", "-m", help="Boolean expression for filtering records")
    parser.add_argument("--fields", "-f", nargs="+", help="Specific tags to output (e.g., 100 245)")
    parser.add_argument("--count", "-c", action="store_true", help="Print match count to terminal")
    
    args = parser.parse_args()
    process_marc(args)