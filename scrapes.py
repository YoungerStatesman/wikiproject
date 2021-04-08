import requests
from bs4 import BeautifulSoup as bs
S = requests.Session()

# Example: Henry James (QID: Q170509)
wp = "https://en.wikipedia.org/w/api.php"
wd = "https://www.wikidata.org/w/api.php"
wpp = {
    "action": "query",
    "titles": "Henry_James",
    "prop": "extracts",
    "format": "json"
    }

# "Jules Am\u00e9d\u00e9e Barbey d'Aurevilly" # Gives an empty BS.text string, maybe because it's an automatic wikipedia redirect? Its id key in the 'pages' dictionary (k) is 47319708.
# "Jules Amédée Barbey d'Aurevilly" # Output by SPARQL, but doesn't actually work, since it turns into a Unicode string, as in the first example. Thus k = 47319708...
# "Jules_Barbey_d%27Aurevilly" # Gives an error at the ...['pages'][k] level ('invalidreason': 'The requested page title contains invalid characters: "%27".'), and k = -1. Thus HTML-coded special characters are illegal.
# "Jules Barbey d'Aurevilly" # Success. k = 151321
# "Jules_Barbey_d'Aurevilly" # Success. k = 151321

class invalid_page_id(Exception):
    pass

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
    text = bs(raw).text
    if text == '':
        raise invalid_page_id("Name passed to API led to a Wikipedia redirect or placeholder page: extract string is empty.")

    return text
