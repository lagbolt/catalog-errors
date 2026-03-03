#
#    Filter MARC records from an input file using boolean logic and regular expressions
#    and write matching records to an output file or display them in the terminal.
#
#    Usage:  python marc-filter.py 
#               --input <MARC input file>       # required
#              [--output <MARC output file>] 
#              [--match <boolean expression>]
#              [--fields <tags>]
#              [--count]
#
#    The --match expression consists of one or match conditions combined with AND, OR, NOT
#    and parentheses.  Each condition is of the form: <tag> [$<subfield>] <regex pattern>.
#    The entire match condition should be enclosed in double quotes.  If the regex pattern
#    contains spaces, it should be enclosed in single quotes.
#
#    For example:
#
#        --match "245 $a Python AND 650 'Computer programming'"
#
#    If --output is not specified, matching records will be printed to the terminal.
#    If --fields is specified, only those tags will be included in the output.
#    If --count is specified, a summary of total records processed and matches found will be printed.
#
#    If you find yourself wishing for something slightly different, please email me.
#
#    Version:  0.1.0  2/26/26
#
#    License:  CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/
#
#    Graeme Williams
#    carryonwilliams@gmail.com

import sys
import re
import argparse
from pymarc import MARCReader, MARCWriter, Record

def check_match(record, field_tag, subfield_code, pattern):
    """Checks if any single field/subfield in a record matches a regex pattern."""
    target_fields = record.get_fields(field_tag)
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

    conditions = []
    eval_logic = "True" # Default to matching everything if no expression
    
     # Setup match logic if a match expression is provided on the command line
    if args.match:

        # This will capture each individual condition in the match expression
        condition_regex = r"(\d{3})\s+(?:\$([a-z0-9])\s+)?('(?:[^'\\]|\\.)*'|\S+)"
        
        def condition_replacer(match):
            # Collect the components of the condition from the regex match
            tag = match.group(1)
            subfield = match.group(2) 
            pattern_raw = match.group(3).strip("'")
            try:
                compiled_re = re.compile(pattern_raw, re.IGNORECASE)
                # Collecting each condition is a side effect of calling this
                # function on each regex match in the expression.
                conditions.append((tag, subfield, compiled_re))
                # Replace the condition in the expression with this text
                return f"__results[{len(conditions)-1}]"
            except re.error:
                print(f"Invalid regex in expression: {pattern_raw}")
                sys.exit(1)

        # This calls condition_replacer for each match in the expression, building the conditions list
        # and replacing each condition in args.match with "__results[i]".  This means that eval_logic
        # ends up as a boolean expression consisting of results[i] items.
        # For example:  "245 $a "Python" AND 650 "Programming"" becomes "__results[0] and __results[1]"
        eval_logic: str = re.sub(condition_regex, condition_replacer, args.match)
        eval_logic = eval_logic.replace("AND", " and ").replace("OR", " or ").replace("NOT", " not ")

    match_count = 0
    total_records = 0

    # Process the MARC file
    with open(args.input, 'rb') as inf:
        reader = MARCReader(inf)
        writer = MARCWriter(open(args.output, 'wb')) if args.output else None
        
        for record in reader:
            if record is None: continue
            total_records += 1
            
            # Evaluate conditions for this record.  This populates the results list with
            # True/False for each filter so it can be used in the eval_logic expression
            results = [check_match(record, t, s, p) for t, s, p in conditions]
            
            # evaluate the boolean expression, substituting for the __results[i] items.
            if eval(eval_logic, {"__builtins__": {}}, {"__results": results}):
                match_count += 1
                
                # Handle output to file
                if writer:
                    if output_tags := args.fields:
                        # Create a record with only requested fields for file output
                        new_rec = Record()
                        new_rec.leader = record.leader
                        for field in record.get_fields(*output_tags):
                            new_rec.add_field(field)
                        writer.write(new_rec)
                    else:
                        writer.write(record)
                
                # Handle output to terminal (if no output file specified)
                else:
                    print(f"--- Record {match_count} ---")
                    if display_tags :=args.fields:
                        for field in record.get_fields(*display_tags):
                            print(field)
                    else:
                        print(record)
        
        if writer:
            writer.close()
    
    if args.count:
        print(f"\nProcessed {total_records} records. Found {match_count} matches.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter and display or save MARC records from the input file.")
    parser.add_argument("--input", "-i", required=True, help="Input MARC file")
    parser.add_argument("--output", "-o", help="Output MARC file (writes to terminal if omitted)")
    parser.add_argument("--match", "-m", help="Boolean expression for filtering records")
    parser.add_argument("--fields", "-f", nargs="+", help="Specific tags to output (e.g., 100 245)")
    parser.add_argument("--count", "-c", action="store_true", help="Print match count to terminal")
    
    args = parser.parse_args()
    process_marc(args)