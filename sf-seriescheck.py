#
#    Scan a MARC file or database table and use the author and title to retrieve series
#    information from various external sources to check for a missing 490 (series) field.
#    Because a downloaded copy of isfdb.com is the primary source, this specific code is
#    only suitable for lists of science fiction and fantasy books. 
#
#    Usage:  python sf-seriescheck.py --inputfile <MARC input file> [ --libcode library-code]
#       or:  python sf-seriescheck.py --inputtable <name of database table>  [ --libcode library-code]
#
#    The database table should have columns for bibnumber, tag, indicators, and tagData.
#    tagData is all the subfields glommed together.  You can get more information from
#    the mydb.py file in the lib folder.
#
#    The --libcode argument is necessary in order to retrieve series data from Novelist.
#    DO NOT include this unless you are a Bibliocommons library using your own
#    library code.
# 
#    Version:  0.1.0  1/1/21
#
#    License:  CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/
#
#    Graeme Williams
#    carryonwilliams@gmail.com
#

from collections import Counter
import argparse
import requests

from lib import mydb, mymarc, opac, goodreads

parser = argparse.ArgumentParser(description=
    """Specify either an input file or a MySQL input table.
        (The database name is hard-coded.  Sorry.)
        --libcode is optional but is needed to check Novelist.
        If it's not included, Novelist checking will be skipped.
    """
    )
parser.add_argument("--libcode", "-lc", required=False)
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("--inputfile", "-if")
group.add_argument("--inputtable", "-it")

args = parser.parse_args()

therecordgenerator = mymarc.recordgenerator(args.inputfile, args.inputtable)
check_cnx = mydb.Connection(schema="isfdb")
check_table = mydb.Table(check_cnx, "author_title_series_name")

# if you don't specify a library code, Novelist will not be checked
libcode = args.libcode

counts = Counter()
session = requests.Session()
limit_counter = 0

# For each MARC record in the file or database table:
#   - collect authors from 100, 700;
#   - run each check in the checkList
for bibnum, theRecord in therecordgenerator:
    if (limit_counter := limit_counter+1) > 10000:
        print("Hit limit from input table!")
        break
    if (field100 := theRecord['100']):
        try:
            author_name = mymarc.flipnames(field100['a']).encode("utf-8", "strict").decode('latin-1', "strict")
            title = theRecord['245']['a'].rstrip("/: ").encode("utf-8", "strict").decode('latin-1', "strict")
        except Exception:
            # print(f"Encoding problem with {field100['a']} or {record['245']['a']}")
            counts['Character conversion failed'] += 1
            continue
        query = (
            f"WHERE author={mydb.dbescape(author_name)}"
            f" AND title={mydb.dbescape(title)}"
        )
        try:
            row = check_table.readfirstrow(query=query, debug=False)
        except Exception:
            # print(f"Problem with {author_name} and {title}")
            counts['Query failed'] += 1
            continue
        
        # At this point, we have the MARC record, from which we have extracted the title and author_name
        # row has been returned from the local ISFDB instance, but might be None
        # We're going to check whether the record has a 490 field and whether row is not None,
        # BUT we're not going to check that the series names match.

        # print(f"Checking {title} (by) {author_name}")
        opac_check = "OPAC:Y" if theRecord["490"] else "OPAC:N"
        db_check = "ISFDB:Y" if row else "ISFDB:N"
        key = "/".join([opac_check, db_check])
        counts[key] += 1

        # We only do further checks for records that, according to ISFDB, have missing
        # series information.  This is to avoid load on Novelist or Goodreads.

        if opac_check == "OPAC:N" and db_check == "ISFDB:Y":
            isfdb_seriesname = row[2]
            # print(f"Missing 490 in {bibnum}: {title} (by) {author_name} = {isfdb_seriesname}")
            if bool(libcode) and bool(bibnum):
                novelist_seriesname = opac.checkNoveListseries(session, libcode, bibnum, requestdelay=5)
            else:
                novelist_seriesname = None
            if goodreads.enabled():
                goodreads_seriesname = goodreads.get_seriesname(session, goodreads.get_worknumber(session, author_name, title))
            else:
                goodreads_seriesname = None
            print(bibnum, author_name, title, isfdb_seriesname, novelist_seriesname, goodreads_seriesname, sep = ',')

print(counts)

session.close()
