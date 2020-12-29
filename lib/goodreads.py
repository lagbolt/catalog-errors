from typing import List
import requests
import xmltodict
import time

##############################################################
# NOTE:  Goodreads has deprecated the API and is no longer
# giving out API keys.  If you want to use this, let's talk.
##############################################################

GOODREADS_API_KEY = "MNlciatZGMcW92q6tRoQA"

# The Goodreads API returns deeply nested XML, so we have to do some
# work to extract the few values we need, first converting to JSON.

def get_worknumber(session, author:str, title:str, debug=False):
    time.sleep(2)
    url = f"https://www.goodreads.com/search/index.xml?key=" + GOODREADS_API_KEY
    params = { 'q' : f"{author} {title}"}
    response = session.get(url, params=params).text
    if (results := xmltodict.parse(response)['GoodreadsResponse']['search']['results']):
        if type((work := results['work'])) == type(list()):
            work = work[0]
        if debug:
            print(f"work in get_worknumber {work}")
        return work['id']['#text']
    else:
        if debug:
            print("No author title match in get_worknumber")
        return None

def get_seriesname(session, worknumber: str, debug=False):
    time.sleep(2)
    url = f"https://www.goodreads.com/work/{worknumber}/series?format=xml&key=" + GOODREADS_API_KEY
    response = session.get(url).text
    seriesworks = xmltodict.parse(response)['GoodreadsResponse']['series_works']
    if debug:
        print(f"seriesworks in get_seriesname:\n{seriesworks}")
    if not seriesworks:
        return None
    serieswork = seriesworks['series_work']
    if type(serieswork) == type(list()):
        serieswork = serieswork[0]
    return serieswork['series']['title']


# This allows you to run this file on it own to test single author/title values.
def _testloop():
    with requests.Session() as session:
        debugFlag = False
        while True:
            response = input("Author (or 'end'): ")
            if response == "end":
                break
            if response == "debug":
                debugFlag = True
                continue
            author = response
            title = input("Title: ")
            if not (worknumber := get_worknumber(session, author, title, debugFlag)):
                print("No such author/title")
                continue
            seriesname = get_seriesname(session, worknumber, debugFlag)
            print(author, title, seriesname)

if __name__ == "__main__":
    _testloop()
