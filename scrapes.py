import requests
from bs4 import BeautifulSoup as bs
import re
import json
from urllib.parse import unquote
import time

S = requests.Session()

# Example: Henry James (QID: Q170509)
wp = "https://en.wikipedia.org/w/api.php"
wd = "https://www.wikidata.org/w/api.php"
qu = "https://query.wikidata.org/sparql"

# Sample parameters
# wpp = {
#     "action": "query",
#     "titles": "Henry_James",
#     "prop": "extracts",
#     "format": "json"
#     }

class invalid_page_id(Exception):
    pass

# Grabs wikipedia article text
def get_text(name):
    wpp = {
    "action": "query",
    "titles": name,
    "prop": "extracts",
    "format": "json"
    }

    k = list(S.get(url="https://en.wikipedia.org/w/api.php", params=wpp).json() ['query'] ['pages'].keys()) [0]
    if k == '-1':
        raise invalid_page_id(f"Illegal characters (probably HTML) in name passed to API: Wikipedia page ID is {k}.")

    raw = S.get(url=wp, params=wpp).json()['query']['pages'][k]['extract']
    text = bs(raw, 'lxml').text
    if text == '':
        raise invalid_page_id("Name passed to API led to a Wikipedia redirect or placeholder page: extract string is empty.")

    return text

# Finds word counts
exc = 0; inc = 1
def countWords(string):
    state = exc; wc = 0
    # Scan characters one by one
    for i in range(len(string)):

        # If next character is a separator, set state to out
        if (string[i] == ' ' or string[i] == '\n' or
                string[i] == '\t'):
            state = exc

        # If next character is not a separator and state is out,
        # set state to in and increment count
        elif state == exc:
            state = inc
            wc += 1

    return wc

# This function issues SPARQL calls to convert an occupation's QID back into a readable label

def get_label(id):
    query = f"SELECT * WHERE {{wd:{id} rdfs:label ?label. FILTER(LANGMATCHES(LANG(?label), 'EN'))}} LIMIT 1"
    resp = S.post(url = qu, params = {'query': query, 'format': 'json'}).text
    label = json.loads(resp)['results']['bindings'][0]['label']['value']
    return label

# Why the safename function:
#
# "Jules Am\u00e9d\u00e9e Barbey d'Aurevilly" (Unicode identifiers)
# Gives an empty BS.text string, maybe because it's an automatic wikipedia redirect? Its id key in the 'pages' dictionary (k) is 47319708.
#
# "Jules Amédée Barbey d'Aurevilly" (Unicode character)
# Output by SPARQL, but doesn't actually work, since it turns into a Unicode string, as in the first example. Thus k = 47319708...
#
# "Jules_Barbey_d%27Aurevilly" (HTML)
# Gives an error at the ...['pages'][k] level ('invalidreason': 'The requested page title contains invalid characters: "%27".'), and k = -1. Thus HTML-coded special characters are illegal.
#
# "Jules Barbey d'Aurevilly" and "Jules_Barbey_d'Aurevilly" (no non-ASCII characters)
# Success. k = 151321
#
# Return query-safe name compatible with wikipedia API calling (using get_name)

def safename(url):
    trunc = re.search("(?<=\/wiki\/).+", url).group()
    safe = unquote(trunc)
    return safe

# This function relabels the final metrics dataframe (whose index is occupation QIDs). I had to enter a sleep delay and a try/except test because using the get_label API call is really fussy for some reason??
def relabel(frame):
    newindex = []
    for i in frame.index:
        try:
            j = get_label(i)
            newindex.append(j)
        except:
            time.sleep(1)
            j = get_label(i)
            newindex.append(j)
    return newindex
