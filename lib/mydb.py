# 
#    Version:  0.1.0  1/1/21
# 
#    License:  CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/
#
#    Graeme Williams
#    carryonwilliams@gmail.com
#

import os
import itertools
from pymarc import Record, Field

if os.environ.get('MU') or os.environ.get('USERDOMAIN') == 'DESKTOP-UPR7L5U':
    import mysql.connector
else:
    import MySQLdb

# Password for pythonanywhere MySQL instance
PA_PASSWORD = "it really isn't this"                  # reminder = sweet factors
LOCAL_PASSWORD = "it isn't this either"               # reminder = anu

def dbescape(s):
    # escape single quotes so data for text columns won't break
    # if it contains single quote
    return("'" + s.replace("'", "\\'") + "'")

class Connection:

    # a moderate amount of argy bargy to check if the connection
    # fell over and reconnect if it did

    def __init__(self, schema=None):
        self.schema = schema
        self._connection = self._open()

    def _open(self):
        if os.environ.get('MU') or os.environ.get('USERDOMAIN') == 'DESKTOP-UPR7L5U':
            if not self.schema:
                raise Exception('Missing schema in dbconnect')
            return mysql.connector.connect(user='graeme', password='gjw497',
                host='127.0.0.1',
                database=self.schema,
                connection_timeout=36000)
        else:  # pythonanywhere, which is the else because it doesn't expose env vars
            return MySQLdb.connect(host="lagbolt.mysql.pythonanywhere-services.com",
            user="lagbolt", password=PA_PASSWORD, database="lagbolt$default",
            charset='utf8', use_unicode=True)

    def get_connection(self):
        if not self._connection.is_connected():
            # blow away existing connection, it's dead, Jim
            self._connection = self._open()
        return self._connection

    def cursor(self):
        return self.get_connection().cursor()

class Table:

    def __init__(self, cnx, name):
        # cnx should be a Connection object (above) so you get
        # automatic reconnection on failure, but a vanilla
        # mysql connection will probably also work fine
        self.cnx = cnx
        self.name = name      

    # this assumes my (non-standard) way of storing MARC records in the database using
    # a separate database record for each field.
    # tagData is all the subfields glommed together (e.g., "$aSmith, Bob$d1995-$fsomething else")
    # If you want a different table  format, change this function and/or readpymarc.
    def readmarc(self, query=""):
        cursor = self.cnx.cursor()
        querycmd = f"SELECT bibNumber, tag, indicator, tagData FROM {self.name} " + query
        cursor.execute(querycmd)
        row = cursor.fetchone()
        while row is not None:
            yield row
            row = cursor.fetchone()

    # returns a tuple consisting of the bibnumber from the database and a standard
    # pymarc Record.  If you switch to a different table format you can use
    # anything for bibnumber as long as it's unique -OR- just return ''.
    def readpymarc(self, query=""):
        # This piece of magic is just to re-assemble the MARC record from its separate
        # fields assuming that the first element of the row returned by readmarc uniquely
        # defines the MARC record.
        # If your database format uses a single database record for the MARC record,
        # you won't need this outer loop.
        for _, dbrecordlist in itertools.groupby(self.readmarc(query), lambda x : x[0]):
            pyrecord = Record()
            bibnumber = ''
            for bn, tag, indicators, tagData in dbrecordlist:
                bibnumber = bn  # doesn't matter that we do this every time
                if tag[0:2] == "00":        # fixed format header field
                    pyrecord.add_field(
                        Field(tag = tag, data = tagData)
                        )
                else:                       # ordinary field
                    subfields = list()
                    merge = ""
                    # tagData is all of the subfields glommed together, separated by $
                    # The [1:] index is used to skip the initial None.
                    for subfield in tagData.split('$')[1:]:
                        if len(subfield) < 2:     # special case for $c$nn.nn 
                            merge = subfield + "$"
                            continue
                        sf = merge + subfield
                        # this next line because pymarc Field.subfields is a list of 
                        # alternating tags and values like:
                        #    [ 'a', 'Turtles', 'b', 'The Real Story', 'c', 'by Bob Smith' ]
                        subfields.extend([sf[0], sf[1:]])
                        merge = ""
                    pyrecord.add_field(
                        Field(
                            tag = tag,
                            indicators = list(indicators),  # turns string into list
                            subfields = subfields
                            )
                        )
            yield bibnumber, pyrecord

######################################################################
#
#  Utility routines unused outside the opac library scraping routines
#
#######################################################################

    def readfirstrow(self, columns = "*", query="", debug=False):
        querycmd = f"SELECT {columns} from {self.name} {query}"
        if debug:
            print(f"Querycmd in readfirstrow is {querycmd}")
        with self.cnx.cursor() as cursor:
            cursor.execute(querycmd)
            all_values = cursor.fetchall()
        return all_values[0] if all_values else None

    def readrow(self, query="", debug=False):
        cursor = self.cnx.cursor()
        querycmd = f"SELECT * from {self.name} " + query
        if debug:
            print(f"Querycmd in readrow is {querycmd}")
        cursor.execute(querycmd)
        row = cursor.fetchone()
        while row is not None:
            yield row
            row = cursor.fetchone() 

    def addmarc(self, bibnum, tag, indicator, tagData):
        cursor = self.cnx.cursor()
        tagDataX = dbescape(tagData)
        insertcmd = f"INSERT into {self.name} (bibnumber, tag, indicator, tagData)" \
            f" VALUES ('{bibnum}', '{tag}', '{indicator}', {tagDataX})"
        # print("Table insertcmd is", insertcmd)
        cursor.execute(insertcmd)
        self.cnx.commit()
        cursor.close()

    def checkfieldvalue(self, field_name, field_value):
        cursor = self.cnx.cursor()
        fv = dbescape(field_value)
        querycmd = f"SELECT {field_name} FROM {self.name} where {field_name} = {fv}"
        try:
            cursor.execute(querycmd)
        except Exception as e:
            print(f"Exception in checkfieldvalue with {querycmd}")
            return False
            # raise e
        row = cursor.fetchall()
        cursor.close()
        return bool(row)

    def uniquevaluesfromtag(self, tag_name):
        cursor = self.cnx.cursor()
        querycmd = f"SELECT distinct tagData from {self.name} where tag = '{tag_name}'"
        cursor.execute(querycmd)
        result = cursor.fetchall()   # list, NOT a generator
        cursor.close()
        return result
