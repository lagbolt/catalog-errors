# Various data files

## seriescheck_Jan2021.xlsx: output from seriescheck.py

This is the data I presented to the ALA Core Cataloging Norms Interest Group on February 1, 2021.  After February 1, 2021, you'll be able to retrieve the slides from https://github.com/lagbolt/writing.

I've zeroed out the bib number column to keep the name of the library private.

## Library of Congress subject term files

lcsh-subject-terms.txt:  Subject terms from the LCSH

This is the output of build-lists.py, for use by sh-check.py.  You can use this for testing, but if you're running this against production data, you should really download up-to-date data from the LoC and rerun the whole workflow.

lcsj-entries.txt:  Subject terms extracted by hand from LC Children's Subject Headings

For use by sh-check.py.  Again, you should download up-to-date data from LoC.
