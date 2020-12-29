import json

outf = open("lcsh-madsrdf-out.txt", 'w', encoding='utf-8')

with open(r"lcsh.madsrdf.ndjson") as inf:
    for c, ln in enumerate(inf):
        json_graph = json.loads(ln)['@graph']
        for json_part in json_graph:
            ks = json_part.keys()
            if (not '@id' in ks
                or not '@type' in ks
                or not 'madsrdf:authoritativeLabel' in ks):
                continue
            id = json_part['@id'].split('/')[-1:][0]
            if id[0:2] != "sh":
                # print(f"skipping non-LCSH id {json_part['@id']}", file=outf)
                continue
            if ('madsrdf:deletionNote' in ks
                or 'madsrdf:DeprecatedAuthority' in json_part['@type']
                or 'madsrdf:Variant' in json_part['@type']):
                # print(f"skipping deleted/deprecated/variant {json_part['@id']}", file=outf)
                continue
            auth_label = json_part['madsrdf:authoritativeLabel']
            if type(auth_label) == list:
                for l in auth_label:
                    sh = l['@value']
                    print(f"#{c} {id} {sh}", file=outf)
            else:
                sh = auth_label['@value']
                print(f"#{c} {id} {sh}", file=outf)
        if c > 999999:
            break

outf.close()

