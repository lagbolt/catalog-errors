# Tools for checking library catalog records

This code requires Python 3.8 (because I use the walrus operator).

In this folder:
* this file
* a requirements.txt file
* Python libraries in the lib folder
* recordscan.py, a console application
* seriescheck.py, a console application
* the LC folder, containing a workflow for checking subject headings

Btw, if you need help, email me!

## A note about checking

The applications in this repository are not perfect.  They do not detect all errors, and not every record they report is actually in error.

An example:  recordscan.py attempts to detect duplicate Name Authority Records by looking for matching names like "Smith, Bob" and "Smith, Bob, 1995-".  In a public library, most of the time this will represent a genuine error, but sometimes this will represent two different people.

This means that a certain amount of hand checking is still necessary.

## The requirements.txt file

First, you'll need to install Python, which should include pip.  Use the requirements.txt file to install the Python libraries needed by the applications:
```
pip install -r requirements.txt
```

## The lib folder

This contains a number of libraries used by the console applications.  The console applications in this folder will find it automatically.  The applications inside the LC folder will find it because of the symbolic link inside that folder.

IF YOU DOWNLOAD A ZIP OF THIS REPOSITORY ON WINDOWS rather than cloning it, the 'lib' symbolic link in the LC folder will be broken and you will have to fix it.

If you want to read data (i.e., MARC records in some form) from a MySQL database you will need to modify mydb.py to connect to your database.  You will also need to supply the database password in secrets.py

## A note about the console applications

You run the console applications using Python, e.g.:
```
python recordscan.py (arguments ...)
```

The console applications will read either from a MARC file (specified by the --inputfile argument) or a MySQL database table (specified by the --inputtable argument).

If you want to read data from a database, you'll need to edit the code in lib\mydb.py to connect to your MySQL database instance.  Once you've done that, you can specify the table with or without the schema name.  That is, "tablename" or "schema.tablename".  If you don't specify a schema, it will use the value used when the code connects to the database.

The format of the table is described in lib\mydb.py.  You can use data in whatever format you like provided you modify mydb.readpymarc to yield a bibnumber (any string to identify the record) and a pymarc Record.

## recordscan.py

This console application reads MARC records one by one and:
* runs a series of error checks against the record, optionally printing out matching (i.e., problematic) records.  The checks are defined in the code, but if you know a little about the pymarc library, you should be able to add your own.
* checks for duplicate names, as described above.

## seriescheck.py

This console application extracts the author, title and any series information from the MARC record and compares this to the series information available from:
* a downloaded copy of ISFDB.com
* Goodreads.com, via their API
* Novelist, via an internal OPAC API

You will only be able to read series data from Goodreads if you supply an API key in lib\secrets.py.  Goodreads has depreceated the API and is no longer giving out keys.  If you would like to use my API key, let's discuss it.

FOr series data from Noevlist, I use an API internal to Bibliocommons OPACs.  You will need to supply a library code on the command line using the --libcode argument.  If it isn't obvious what the code is, email me.

I don't compare every record to all three sources since I don't want to overload the Goodreads or Novelist APIs.  I compare the record to the downloaded copy of ISFDB.com.  If there's *any* series information in ISFDB and no 490 in the record, then I go on to check Goodreads and Novelist, and report the results for all three sources.

This means that there might be records which are missing series information which are not reported, if the information is also missing in ISFDB.

## The LC folder

This folder has its own README.md.  In brief, the folder contains a workflow for checking 6xx fields against data from the Library of Congress.

