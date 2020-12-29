# Checking MARC subject headings against the Library of COngress

This is a lot of steps.  Well, not really, only five.  It's partly for efficiency, partly for debugging, and partly in case you find other uses for the intermediate files.

Btw, if anything isn't clear, send me email.

## Step 0

You should arrange to have the lib folder from this repository somewhere in Python's library search path (e.g., by adding the repo folder to PYTHONPATH).  At a minimum, you can type:
```
set PYTHONPATH=%PYTHONPATH%;..
```
or the Unix equivalent before you run any of the applications below

## Step 1

Download and unzip lcsh.madsrdf.ndjson from the Library of Congress (https://id.loc.gov/download/).  The file is called "LC Subject Headings (LCSH) \*NEW Pilot\* (MADS/RDF only)"

## Step 2

Run scan-madsrdf-json.py

This will read lcsh.madsrdf.ndjson and write subject headings into the file lcsh-madsrdf-out.txt

You'll see that each line of the file includes the line number from the input file, the LoC reference number, and the subject heading.

## Step 3

Run build-lists.py

This will read lcsh-madsrdf-out.txt and write out two files, lcsh-phrases.txt and lcsh-words.txt, which I will explain by example ...

Suppose one line of the input is:
```
#NNN shNNNNNN Battles, Boring--Marsupials, Australian
```
then "Battles, Boring" and "Marsupials, Australian" would be added to the lcsh-phrases.txt file, and each word would be added to the words file.

(The words file is not actually used in this workflow.)

## Step 4

Run sh-check.py

This program can read either from a MySQL database table or a MARC file.  If you're reading from a MySQL database you'll need to edit the connection information in mydb.py

The table can be specified either by name or by schema and name (e.g., "schema_name.table_name").

The program will check the subject headings in the 6xx fields of the input with the LoC subject headings and list fields where there is a discrepancy.

The program will list each bad heading once, and also provide a summary with counts.  If you want every occurrence of a bad heading listed, you'll need to edit the code (specifically the errorSet variable).

The output is a bit idiosyncratic.  A code is appended to each subfield, as follows:
    Y - found in the LCSH
    C - found in the LC children's headings
    N - not found
    D - a date
    I - ignored
    FC - for the phrase "Fictitious character"

## Known issues

Subfield values should also be checked against the LCNAF.  Since this is not done, there are a passel of false hits from names and titles which are legal but do not appear in the LCSH.
