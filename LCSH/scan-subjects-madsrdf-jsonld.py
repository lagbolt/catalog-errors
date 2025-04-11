#
#    Scan a Library of Congress subject heading file and extract the subject headings.
#
#    The input file is the unzipped version of the file subjects-madsrdf-jsonld.gz
#    downloaded from https://id.loc.gov/download/.
#
#    The workflow of which this is a part is described in the accompanying README.md file.
#
#    Usage:  python scan-subjects-madsrdf-jsonld.py subjects.madsrdf.jsonld subject-entries.txt
# 
#    Version:  0.2.0  4//8/25
#  
#    License:  CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/
#
#    Graeme Williams
#    carryonwilliams@gmail.com
# 

import json
from rich.pretty import pprint
from sys import argv

def process_primary(item, line_number, outfile, type_list = None):
    # This is the primary node in the graph
    if type_list and all([atype not in item['@type'] for atype in type_list]):
        # either type_list is None or we don't want this node type
        return
    key = item.get('bflc:marcKey', 'xxx')[0:3]  # 'xxx' if no marcKey value
    id = item['@id'].split('/')[-1]
    # handle difference between LCSH and LCNAF
    if isinstance(item['madsrdf:authoritativeLabel'], str):
        authoritative_label = item['madsrdf:authoritativeLabel']
    elif isinstance(item['madsrdf:authoritativeLabel'], dict):
        authoritative_label = item['madsrdf:authoritativeLabel']['@value']
    else:
        # unexpected JSON format
        print("Error parsing authoritativeLabel")
        pprint(item)
        exit()
    print(f"{line_number+1:6} {id:16}", key, authoritative_label, file=outfile)

arg_list = argv[3:] if len(argv) > 3 else None

with (open(argv[1], 'r', encoding='utf-8') as f,
    open(argv[2], 'w', encoding='utf-8') as out):
    for line_number, aline in enumerate(f):
        data = json.loads(aline)
        graph = data['@graph']
        for item in graph:
            if ('madsrdf:DeprecatedAuthority' in item['@type']
                or 'madsrdf:deletionNote' in item):
                # print(f"{line_number+1:6} {id:16}" 'Deprecated/Deleted', file=out)
                # skip this entry entirely
                break
            elif 'bflc:marcKey' in item or 'identifiers:lccn' in item:
                process_primary(item, line_number, out, arg_list)
                break
        else:
            print("Couldn't find a primary node")
            pprint(graph)
            exit()