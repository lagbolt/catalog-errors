#
#    Read a file of Library of Congress control numbers, one per line, downloads the
#    corresponding records in MARCXML format from id.loc.gov, and write the MARCXML to a file.
#
#    Usage:  python lccn-to-marcxml.py <input-file> <output-file>
#
#    For example, if one line of the input file is "no2015128232", the MARCXML is downloaded
#    from https://id.loc.gov/authorities/names/no2015128232.marcxml.xml
#
#
#    Version:  0.1.0  6/25/25
#
#    License:  CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/
#
#    Graeme Williams
#    carryonwilliams@gmail.com
#


import requests
import sys
import time


# As required by id.loc.gov/robots.txt
REQUIRED_DELAY = 3  # seconds

# Needed for MarcEdit
xmlpreamble = """\
<?xml version="1.0" encoding="UTF-8" ?>\
<marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim" \
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \
xsi:schemaLocation="http://www.loc.gov/MARC21/slim http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd">"""

xmlpostamble = "</marc:collection>"

if len(sys.argv) < 3:
    print("""Usage: python lccn-to-marcxml.py <input-file> <output-file>\n
    Input file is a list of LC numbers (e.g., no2015128232) one per line.
    Output file is MARC XML which MarcEdit should accept.""")
    exit(1)

with open(sys.argv[1], "r") as input_file:
    with open(sys.argv[2], "w") as output_file:
            output_file.write(xmlpreamble)
            for line in input_file:
                line = line.strip()
                if line.startswith("#"):
                    continue
                url = "https://id.loc.gov/authorities/names/" + line + ".marcxml.xml"
                # print(url)         # just for debugging
                response = requests.get(url)
                if response.status_code == 200:
                    output_file.write(response.text + "\n")
                else:
                    print(f"Error {str(response.status_code)} for {url}")
                time.sleep(REQUIRED_DELAY)
            output_file.write(xmlpostamble)