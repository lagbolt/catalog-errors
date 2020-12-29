import requests
import re
import time

#--------------------------
#
#  Utility functions
#
# -------------------------

DEFAULTDELAY = 3

# 'old' format is all digits with the system number at the end
# 'new' format is SnnnCnnnnnnnn
def bibnumformat(input_str:str, format:str) -> str:
    if format=="new":
        if input_str[0]=="S":   # already in new format
            return input_str
        else:
            return f"S{input_str[-3:]}C{input_str[:-3]}"
    else:
        if input_str[0] != "S":   # already in old format
            return input_str
        else:
            s_part, c_part = input_str[1:].split("C")
            return c_part+s_part

def extractbibnum(m: re.match) -> str:
    if m.lastindex == 1:       # 'old' format
        return m.group(1)
    else:                      # 'new format
        # prefix zeroes if system number < 3 characters         
        return m.group(2) + ("000"+m.group(1))[-3:]

pagination_pattern = re.compile(r"""
    (?:<span\ data-key="pagination-text"[^>]*>   # identify correct HTML element
    ([\d,]*)[^\d]*([\d,]*)[^\d]*([\d,]*))        # nn to nn of nn -- nn can contain commas
    """, re.VERBOSE)

def checkiflastpage(pagetext, debug=False) -> bool:
    m = pagination_pattern.search(pagetext)
    if m:
        if debug:
            print(m.group(1), m.group(2), m.group(3), sep=" : ")
        return (m.group(2) == m.group(3))        # this is a string comparison
    else:
        if debug:
            print("No pagination text")
        return True

def html_find(source, target, start_pos = 0):
    s1 = source.find(target, start_pos)
    if s1 == -1:
        return None, 0
    # print(f"s1 is {s1}")
    s2 = source.find(">", s1+len(target))
    if s2 == -1:
        return None, 0
    # print(f"s2 is {s2}")
    e = source.find("<",s2+1)
    if e == -1:
        return None, 0
    # print(f"e is {e}")
    return(source[s2+1:e], e)

# ----------------------------------------------------
#
#  OPAC scraping functions for Bibliocommons libraries
#
# -----------------------------------------------------

def searchgenerator(session, query, requestdelay = DEFAULTDELAY, startpage = 1, cookies = None, debug=False):
    page = startpage
    bibset = set()       # used to avoid duplicates.

    while True:
        time.sleep(requestdelay)
        url = query + f"&pagination_page={page}"
        if debug:
            print("--- url is", url)
        rt = session.get(url, cookies=cookies).text

        for m in re.finditer(r'(?:/item/show/(\d*))', rt, flags=re.S):
            bibnumber = extractbibnum(m)
            if bibnumber in bibset:
                continue
            bibset.add(bibnumber)
            if debug:
                print(f"Found {bibnumber} on page {page}")
            yield m   # a match object

        if debug:
            print(f"Dropping to section two on page {page}")
            
        for m in re.finditer(r'(?:\{"id":"S(\d*)C(\d*))', rt, flags=re.S):
            bibnumber = extractbibnum(m)
            if bibnumber in bibset:
                continue
            bibset.add(bibnumber)
            yield m   # a match object

        if checkiflastpage(rt, True):
            return

        page += 1

def getmarcgenerator(session, libcode, bibnumber, requestdelay=DEFAULTDELAY):

    time.sleep(requestdelay)
    url = f"https://{libcode}.bibliocommons.com/item/catalogue_info/{bibnumber}"
    rt = session.get(url).text

    mtag, pos = html_find(rt, r'"marcTag"><str', 0)
    while mtag is not None:
        indicator, pos = html_find(rt, "marcIndicator", pos)
        tagData, pos = html_find(rt, "marcTagData", pos)
        # print("-----------")
        # print(mtag, indicator, tagData)
        yield (mtag, indicator, tagData)
        mtag, pos = html_find(rt, r'"marcTag"><str', pos)

# ----------------------------------------------------------------
#
#  Get series information for a given bibnumber from Novelist.
#
#  DO NOT USE THIS ROUTINE UNLESS YOU ARE A BIBLIOCOMMONS LIBRARY
#  CALLING YOUR OWN GATEWAY.
#
# -----------------------------------------------------------------

def checkNoveListseries(session, libcode, bibnumber, requestdelay=DEFAULTDELAY) -> str:

    time.sleep(requestdelay)
    bn = bibnumformat(bibnumber, "new")
    url = f"https://gateway.bibliocommons.com/v2/libraries/{libcode}/bibs/{bn}/seriesinfo"
    rj = session.get(url).json()

    return rj["seriesInfo"].get("seriesTitle")
