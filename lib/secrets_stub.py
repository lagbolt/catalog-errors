#
#    This is a dummy secrets file.  Values are explained below.
#
#    DO NOT PUT PASSWORDS IN THIS FILE!!
#    --> create a new file called secrets.py and
#        assign values in that file
#

# This is used only in seriescheck.py.  If you don't have a key
# and this remains "", checking your series data against
# Goodreads will be skipped
GOODREADS_API_KEY = ""

# Only needed if you read data from a MySQL database.
# If you only read from MARC files, you're all set.
MYSQL_PASSWORD = ""