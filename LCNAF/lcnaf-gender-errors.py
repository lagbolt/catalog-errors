#
#    Scan a Library of Congress subject heading file and check
#    the gender values from PersonalName records for errors.
#
#    An error is defined as any value which is not included in the list
#    of acceptable values, ignoring anything in parentheses at the 
#    beginning of the value, as well as leading and trailing blanks.

#    The input and output filenames are fixed.
#
#    The input file is the unzipped version of the file
#    "LC Name Authority File (LCNAF) *NEW Pilot* (MADS/RDF only)"
#    in ndjson format downloaded from https://id.loc.gov/download/.
#
#    The output files are described in the accompanying README.md
# 
#    Version:  0.1.0  4/12/21
#  
#    License:  CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/
#
#    Graeme Williams
#    carryonwilliams@gmail.com
# 
import json
from collections import Counter

DEBUG=False

acceptable = [ "male", "males", "man", "men", "female", "females", "woman", "women", "not known"]

# strip parenthetical label and spaces, convert to lower case,
# then check if gender is in acceptable list
def gender_fail(gender_value):
    t = gender_value.strip()
    if t.startswith("("):
        pos = t.find(")") + 1
        t = t[pos:].lstrip()
    return not (t.lower() in acceptable)

# For output in an Excel-compatible .csv file
def quote(s):
    return '"' + s.replace('"', '""') + '"'

# Convert any id which is local to the record (not a URL)
# to the fixed value '@local'
def convert_local(id):
    return id if id.startswith("http") else "$local"

# Collapse a list of identical items into a one item list
def collapse(alist):
    return [ alist[0] ] if all([x == alist[0] for x in alist]) else alist

#
# Find the URI that identifies this record
#
def find_uri(whole_graph):
    for element in whole_graph:
        if (uri := element.get('@id',"")).startswith("http://id.loc.gov/authorities/names/n"):
            return uri
    return "no uri"
#
# Scan an object for the element with the gender attribute, and if
# found pass the attribute to gender_fail for checking
#
def gender_search(whole_graph, outfile):
    global debugstring
    for element in whole_graph:
        if (("http://xmlns.com/foaf/0.1/Person" in element.get('@type', ""))
                and (gender_value := element.get('madsrdf:gender', None))
            ):
            debugstring = str(element)
            gender_check(gender_value, json_graph, outfile)
            return
    return # no gender, no problem

# The value of a gender attribute can either be a one-item dictionary
# (with key = '@id') or a list of one-item dictionaries.  The value in
# the dictionary is NOT the gender value itself, but a key to it.
def gender_check(gender_attribute, whole_graph, outfile):
    global debugstring
    # print("Gender capture", gender_atttribute)
    if isinstance(gender_attribute, list):
        sorted_keys = sorted( [ x['@id'] for x in gender_attribute ] )
        gender_key_list = [ convert_local(id) for id in sorted_keys ]
        gender_value_list = [ decode_key(id, whole_graph) for id in sorted_keys ]
        if any( [ gender_fail(gv) for gv in gender_value_list] ):
            uri = quote(find_uri(whole_graph))
            source_string = quote('+'.join(collapse(gender_key_list)))
            gender_string = quote('+'.join(collapse(gender_value_list)))
            print(uri, source_string, gender_string, sep=" , ", file=outfile)
            if DEBUG:
                print(debugstring, file=outfile)
            # _ = input("CR to continue #1: ")
        # else no fail, not problem
    else:
        key = gender_attribute['@id']
        gender_value = decode_key(key, whole_graph)
        if gender_fail(gender_value):
            print(
                    quote(find_uri(whole_graph)),
                    quote(convert_local(key)),
                    quote(gender_value),
                    sep=" , ", file=outfile
                )
            if DEBUG:
                print(debugstring, file=outfile)
            # _ = input("CR to continue #2: ")
        # else no fail, no problem

# The value of a gender id is given in the element of the graph which
# has an id attribute equal to the gender id attribute
def decode_key(gender_id, whole_graph):
    global debugstring
    # print("Decode key ", gender_id)
    for part in whole_graph:
        if gender_id == part.get("@id"):                
            if gender_value := (part.get("rdfs:label") or part.get("madsrdf:authoritativeLabel")):
                debugstring += " " + str(part)
                return gender_value
            else:
                print("Can't get value from ", part)
                raise Exception("Can't get value from gender object")
    print("Can't find gender id", gender_id)
    print(json.dumps(whole_graph, indent=2))
    raise Exception("Gender id not found")

#
#     Scan input file and print out gender errors
#
if DEBUG:
    outputfilename = "lcnaf-gender-debug.txt"
else:
    outputfilename = "lcnaf-gender-errors.csv"

with open(outputfilename, 'w', encoding='utf-8') as outf:
    with open(r"lcnaf") as inf:
        for i, ln in enumerate(inf):
            # each line in the file is a separate JSON-LD object
            # representing an single name authority record
            json_graph = json.loads(ln)['@graph']
            # Check to see if this object is a Personal Name
            for element in json_graph:
                # If specified, element type is a list of strings
                if ((typelist := element.get('@type'))
                        and ('madsrdf:PersonalName' in typelist)
                        and ('madsrdf:Authority' in typelist)
                    ):
                    # At this point, we know this object is a Personal Name,
                    # so we look for the element with the gender attribute
                    gender_search(json_graph, outf)
                    break
            if DEBUG and (i > 100000):
                break