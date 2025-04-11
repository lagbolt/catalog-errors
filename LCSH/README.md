# Checking MARC subject headings against the Library of Congress

This is a lot of steps.  Well, not really, only five.  It's partly for efficiency, partly for debugging, and partly in case you find other uses for the intermediate files.

Btw, if anything isn't clear, send me email.

## Step 0

Make sure you have a copy of the 'lib' folder in the same  folder as the LCSH folder

## Step 1

Download and unzip lcsh.madsrdf.jsonld.gz from the Library of Congress (https://id.loc.gov/download/).  This will create a file called subjects.madsrdf.jsonld

## Step 2

Run scan-subjects-madsrdf-jsonld.py twice.

First, run it with arguments:

    subjects.madsrdf.jsonld subject-entries.txt

to create the file subject-entries.txt

And second with the arguments:

     childrensSubjects.madsrdf.jsonld childrens-entries.txt

to create the file childrens-entries.txt

You'll see that each line of the output files includes the line number from the LoC input file, the LoC reference number, the MARC tag from the LoC entry, and the subject heading.

## Step 3

Run build-lists.py twice.

First, with the arguments:

     subject-entries.txt subject-terms.txt

to create the file subject-terms.txt

And second with the arguments:

     childrens-entries.txt childrens-terms.txt

to create the file childrens-terms.txt

I'll exmplain what the program does using an example.  Suppose one line of the input is:
```
lineNNNNN shNNNNNN 150 Battles, Boring--Marsupials, Australian
```
then "Battles, Boring" and "Marsupials, Australian" would be added to the terms output file.

(optionally, the program can create a file of all the words in the input, but that functionality
is not used in this workflow.)

## Step 4

Run subjects-check.py.  See the file itself for details of the command arguments.

Note that the names of the files used to load terms are fixed.

This program can read either from a MySQL database table or a MARC file.  If you're reading from a MySQL database you'll need to edit the connection information in mydb.py and supply the database password in secrets.py.  If you're only reading from MARC files, you do not have to make either of those changes.

The table can be specified either by name or by schema and name (e.g., "schema_name.table_name").

The program will check the subject headings in the 6xx fields of the input against the LoC subject terms in the subject-terms.txt file and in the lcsj-entries.txt file and print out fields where there is a discrepancy.

For testing purposes, subject-terms.txt and lcsj-entries.txt files are provided in the files folder of this repository.  However, if you are running this in production, you should probably download up-to-date files from the Library of Congress
and rerun this workflow from the beginning.

The program will list each 'bad' heading once, and also provide a summary with counts.  If you want every occurrence of a bad heading listed, you'll need to edit the code (specifically the errorSet variable).

The output is a bit idiosyncratic.  A code is appended to each subfield, as follows:
* Y - found in the LCSH
* C - found in the LC children's headings
* N - not found
* D - a date
* I - ignored
* FC - for the phrase "Fictitious character"

## Known issues

Subfield values should also be checked against the LCNAF.  Since this is not done, there are a passel of false hits from names and titles which are legal but do not appear in the LCSH.
