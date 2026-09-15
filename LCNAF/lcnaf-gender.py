#
#    Scan a Library of Congress subject heading file and extract
#    the gender values from PersonalName records.

#    The input and output filenames are fixed.
#
#    The input file is the unzipped version of the file
#    "LC Name Authority File (LCNAF) *NEW Pilot* (MADS/RDF only)"
#    in ndjson format downloaded from https://id.loc.gov/download/.
#
#    The output files are described in the accompanying README.md
# 
#    Version:  0.1.0  4/11/21
#  
#    License:  CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/
#
#    Graeme Williams
#    carryonwilliams@gmail.com
# 
import json

from collections import Counter

DEBUG = False
genders = Counter()

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
# Scan an object for the element with the gender attribute, and if
# found pass the attribute to gender_count for counting
#
def gender_search(whole_graph):
    for element in whole_graph:
        if (("http://xmlns.com/foaf/0.1/Person" in element.get('@type', ""))
                and (gender_value := element.get('madsrdf:gender', None))
            ):
            gender_count(gender_value, json_graph)
            return
    genders[("", "$Gender missing")] += 1

# The value of a gender attribute can either be a one-item dictionary
# (with key = '@id') or a list of one-item dictionaries.  The value in
# the dictionary is NOT the gender value itself, but a key to it.
def gender_count(gender_atttribute, whole_graph):
    # print("Gender capture", gender_atttribute)
    if isinstance(gender_atttribute, list):
        sorted_keys = sorted( [ x['@id'] for x in gender_atttribute ] )
        gender_key_list = [ convert_local(id) for id in sorted_keys ]
        gender_value_list = [ decode_key(id, whole_graph) for id in sorted_keys ]
        key_part1 = '+'.join(collapse(gender_key_list))
        key_part2 = '+'.join(collapse(gender_value_list))
        genders[ ( key_part1, key_part2 ) ] += 1
    else:
        key = gender_atttribute['@id']
        genders[ ( convert_local(key), decode_key(key, whole_graph) ) ] += 1

# The value of a gender id is given in the element of the graph which
# has an id attribute equal to the gender id attribute
def decode_key(gender_id, whole_graph):
    # print("Decode key ", gender_id)
    for part in whole_graph:
        if gender_id == part.get("@id"):                
            if gender_value := (part.get("rdfs:label") or part.get("madsrdf:authoritativeLabel")):
                return gender_value
            else:
                print("Can't get value from ", part)
                raise ValueError("Can't get value from gender object")
    print("Can't find gender id", gender_id)
    print(json.dumps(whole_graph, indent=2))
    raise ValueError("Gender id not found")

#
#     Scan input file and collect gender counts
#
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
                gender_search(json_graph)
                break

        # for debugging, because the LCNAF has millions of records
        if DEBUG and not (i%1000):
            print()
            for (k1, k2), cnt in genders.items():
                print(quote(k1), quote(k2), cnt, sep=" , ")
            _ = input("CR to continue: ")

#
#      Output the gender counts in two ways
#
with open("lcnaf-genders-detail.csv", 'w', encoding='utf-8') as outf:
    for (k1, k2), cnt in genders.items():
        print(quote(k1), quote(k2), cnt, sep=" , ", file=outf)

# recount genders counter without first part of key
simple = Counter()
for (k1, k2), cnt in genders.items():
    simple[k2] += cnt

with open("lcnaf-genders-simple.csv", 'w', encoding='utf-8') as outf:
    for k, cnt in simple.items():
        print(quote(k), cnt, sep=" , ", file=outf)


