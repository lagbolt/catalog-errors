#
#    Filter MARC records from an input file using boolean logic and regular expressions
#    and write matching records to an output file or display them in the terminal.
#
#    Usage:  python marc-filter.py 
#               --input <MARC input file>       # required
#              [--output <MARC output file>] 
#              [--match <boolean expression>]
#              [--fields <tags>]
#              [--show-matches]
#              [--quiet]
#              [--count]
#
#    The --match expression consists of one or match conditions combined with AND, OR, NOT
#    and parentheses.  Each condition is of the form: <tag> [$<subfield>] <regex pattern>.
#    Use 'X' as a wildcard in the tag (e.g. 65X matches 650-659).
#    The entire match condition should be enclosed in double quotes.  If the regex pattern
#    contains spaces, it should be enclosed in single quotes.
#
#    For example:
#
#        --match "245 $a Python AND 650 'Computer programming'"
#        --match "65X frog"
#
#    If --output is not specified, matching records will be printed to the terminal.
#    If --fields is specified, only those tags will be included in the output; use 'X'
#    as a wildcard in a tag (e.g. 65X matches 650-659).
#    If --show-matches is specified (terminal output only), fields that satisfied the
#    --match conditions are also printed, in addition to any fields listed in --fields.
#    If --quiet is specified, matched records are not printed or written at all; combine
#    with --count to get only a count of matches, with no record output.
#    If --count is specified, a summary of total records processed and matches found will be printed.
#
#    If you find yourself wishing for something slightly different, please email me.
#
#    Edited by Claude.
#
#    Version:  0.3.0  9/15/26
#
#    License:  CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/
#
#    Graeme Williams
#    carryonwilliams@gmail.com

import sys
import re
import argparse
from pymarc import MARCReader, MARCWriter, Record

def compile_tag_pattern(tag_spec):
    """Compiles a 3-character MARC tag spec into a regex; 'X' matches any single digit."""
    pattern = "".join("[0-9]" if ch.upper() == "X" else re.escape(ch) for ch in tag_spec)
    return re.compile(f"^{pattern}$")

def check_match(record, tag_pattern, subfield_code, pattern):
    """Returns the fields whose tag matches tag_pattern and whose value matches pattern."""
    matches = []
    for field in record.fields:
        if not tag_pattern.match(field.tag):
            continue
        if subfield_code:
            sub_values = field.get_subfields(subfield_code)
            if any(pattern.search(val) for val in sub_values):
                matches.append(field)
        else:
            if pattern.search(field.value()):
                matches.append(field)
    return matches

def parse_match_expression(match_str):
    """Parses a --match expression into a list of (tag_pattern, subfield, value_pattern)
    conditions and an eval-ready boolean expression string referencing __results[i]."""
    conditions = []

    # This will capture each individual condition in the match expression.  The tag may
    # contain digits or 'X' as a wildcard, e.g. 245, 65X.
    condition_regex = r"([0-9Xx]{3})\s+(?:\$([a-z0-9])\s+)?('(?:[^'\\]|\\.)*'|\S+)"

    def condition_replacer(match):
        # Collect the components of the condition from the regex match
        tag_spec = match.group(1)
        subfield = match.group(2)
        pattern_raw = match.group(3).strip("'")
        try:
            compiled_re = re.compile(pattern_raw, re.IGNORECASE)
        except re.error:
            print(f"Invalid regex in expression: {pattern_raw}")
            sys.exit(1)
        # Collecting each condition is a side effect of calling this function on
        # each regex match in the expression.
        conditions.append((compile_tag_pattern(tag_spec), subfield, compiled_re))
        # Replace the condition in the expression with this text
        return f"__results[{len(conditions)-1}]"

    # This calls condition_replacer for each match in the expression, building the conditions list
    # and replacing each condition in match_str with "__results[i]".  This means that eval_logic
    # ends up as a boolean expression consisting of results[i] items.
    # For example:  "245 $a "Python" AND 650 "Programming"" becomes "__results[0] and __results[1]"
    eval_logic = re.sub(condition_regex, condition_replacer, match_str)
    eval_logic = eval_logic.replace("AND", " and ").replace("OR", " or ").replace("NOT", " not ")
    return conditions, eval_logic

def get_matching_fields(record, tag_specs):
    """Returns the record's fields whose tag matches any of the given tag specs
    (each of which may use 'X' as a wildcard, e.g. 65X)."""
    tag_patterns = [compile_tag_pattern(spec) for spec in tag_specs]
    return [field for field in record.fields if any(p.match(field.tag) for p in tag_patterns)]

def build_output_record(record, output_tags):
    """Creates a copy of a record containing only the specified fields."""
    new_rec = Record()
    new_rec.leader = record.leader
    for field in get_matching_fields(record, output_tags):
        new_rec.add_field(field)
    return new_rec

def write_matched_record(record, writer, output_tags):
    """Writes a matched record to the output MARC file."""
    if output_tags:
        writer.write(build_output_record(record, output_tags))
    else:
        writer.write(record)

def print_matched_record(record, results, record_num, display_tags, show_matches):
    """Prints a matched record to the terminal."""
    print(f"--- Record {record_num} ---")

    if not display_tags:
        print(record)
        return

    printed = set()
    for field in get_matching_fields(record, display_tags):
        print(field)
        printed.add(id(field))

    # Also print any fields that satisfied the --match conditions,
    # skipping ones already shown above via --fields.
    if show_matches:
        for matched_fields in results:
            for field in matched_fields:
                if id(field) not in printed:
                    print(field)
                    printed.add(id(field))

def process_marc(args):

    # Default to matching everything if no --match expression is given
    conditions, eval_logic = parse_match_expression(args.match) if args.match else ([], "True")

    match_count = 0
    total_records = 0

    # Process the MARC file
    with open(args.input, 'rb') as inf:
        reader = MARCReader(inf)
        writer = MARCWriter(open(args.output, 'wb')) if args.output else None

        for record in reader:
            if record is None: continue
            total_records += 1

            # Evaluate each condition for this record.  Each entry in results is the (possibly
            # empty) list of fields that satisfied that condition; eval_logic treats an empty
            # list as False and a non-empty list as True.
            results = [check_match(record, tag_pattern, sub, pat) for tag_pattern, sub, pat in conditions]

            if eval(eval_logic, {"__builtins__": {}}, {"__results": results}):
                match_count += 1

                if not args.quiet:
                    if writer:
                        write_matched_record(record, writer, args.fields)
                    else:
                        print_matched_record(record, results, total_records, args.fields, args.show_matches)

        if writer:
            writer.close()

    if args.count:
        print(f"\nProcessed {total_records} records. Found {match_count} matches.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter and display or save MARC records from the input file.")
    parser.add_argument("--input", "-i", required=True, help="Input MARC file")
    parser.add_argument("--output", "-o", help="Output MARC file (writes to terminal if omitted)")
    parser.add_argument("--match", "-m", help="Boolean expression for filtering records")
    parser.add_argument("--fields", "-f", nargs="+", help="Specific tags to output, 'X' wildcards a digit (e.g., 100 65X)")
    parser.add_argument("--show-matches", "-s", action="store_true", help="Also print fields that matched --match, in addition to --fields")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress printing/writing matched records (use with --count for just a count)")
    parser.add_argument("--count", "-c", action="store_true", help="Print match count to terminal")

    args = parser.parse_args()
    process_marc(args)
