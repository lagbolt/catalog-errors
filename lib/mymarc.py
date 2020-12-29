import pymarc

from lib import mydb

#####  Handling names from 100 and 700 fields  #####

# Author names are stored as a tuple, either ( name ), ( name, birthdate ) or ( name, birthdate, deathdate ).
# We use this format instead of, e.g.,  ( name, None, None ) because the latter breaks sorting of tuples
#
# The name is a string either forwards or backwards:  Bob Smith or Smith, Bob.

def namestrip(authorname : str) -> str:
    t = authorname.strip(' ')
    t = t.rstrip(',')
    # strip trailing . unless it's an initial, like "Smith, A."
    if len(t) > 2 and t[-3].isalpha():
        t = t.rstrip('.')
    return t

def flipnames(lastnamefirst:str) -> str:
    lastname, firstnames = lastnamefirst.split(',', 1)  # split only on the first comma
    return namestrip(firstnames) + lastname

def namefromMARC(subfield_a, subfield_d, flip = False) -> tuple:      # subfield_d can be None
    # strip punctuation from subfield a
    t = ( flipnames(subfield_a) ) if flip else ( namestrip(subfield_a) )
    # any punctuation weirdness in subfield d will be carried forward
    if subfield_d:
        dates = subfield_d.split('-')                   # either one date + '' or two dates
        return t + tuple( [ d for d in dates if d ] )   # drop '' if any
    else:
        return t

#####  Handling input streams (file or DB)  #####

# wrapper so reading MARC files looks the same as reading the database:
def readfromfile(filename):
    with open(filename, 'rb') as marc_input:
        for aRecord in pymarc.MARCReader(marc_input):
            # if you have a MARC field you want to use to identify the record
            # assign it to bibnumber here -- as a string
            bibnumber = ""
            yield bibnumber, aRecord

# depending on the input, make a generator out of a MARC
# input file or a database table
def recordgenerator(inputfile:str, dbtable:str):
    if inputfile:
        return readfromfile(inputfile)
    else:
        input_cnx = mydb.Connection(schema="world")
        input_table = mydb.Table(input_cnx, dbtable)
        return input_table.readpymarc(query="")