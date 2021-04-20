#import os
#os.chdir("C://brain//rutgers//564//wikiproject")

from scrapes import *
import pandas as pd

def sparql_table(low, high, *occs):
    dtmin = str(pd.to_datetime(low, format="%Y").date())
    dtmax = str(pd.to_datetime(high, format="%Y").date())
    # print(occs)
    occstr = ""
    if len(occs) == 0:
        return "Stop! You need to pass at least 1 (but maybe at least 2 depending on generality) occupation QIDs."

    for occnum in range(len(occs)):
        if occnum == len(occs)-1:
            occstr += f"wd:{str(occs[occnum])}"
        else:
            occstr += f"wd:{str(occs[occnum])}, "

    # print(occstr)
    # literary critic = Q4263842 ; novelist = Q6625963
    query = f"SELECT DISTINCT ?personLabel ?person ?birth ?article WHERE {{?person wdt:P106 {occstr}; wdt:P569 ?birth. ?article schema:about ?person; schema:isPartOf <https://en.wikipedia.org/>; schema:inLanguage 'en'. FILTER((?birth > '{dtmin}'^^xsd:dateTime) && (?birth < '{dtmax}'^^xsd:dateTime)) SERVICE wikibase:label {{ bd:serviceParam wikibase:language '[AUTO_LANGUAGE],en'. }}}} ORDER BY (?birth)"
    resp = S.post(url = qu, params = {'query': query, 'format': 'json'}).text
    out = json.loads(resp)

    data = {}

    for i in out['results']['bindings'][0].keys():
        data[i] = []

    for i in out['results']['bindings']:
        for j in range(len(i.keys())):
            k = list(i.keys())[j]
            data[k].append(i[k]['value'])

    table = pd.DataFrame(data)
    table['personLabel'] = table['article'].apply(safename)
    table['QID'] = list(map(lambda i : re.search("(?!\/)Q\d+", i).group(), table.person))
    return table

# Test of imported functions

# Q170509 = Henry James (Example)
# safename("https://en.wikipedia.org/wiki/James Joyce")
# countWords("The rain in Spain stays mainly in the plain.")
# get_label("Q170509")
# countWords(get_text(get_label('Q170509')))

# %%

# Outputs dataframe based on the input range for birth dates (e.g. 1800-1900) and their occupation labels,
# which are implicitly separated by AND in the SPARQL query (e.g. critic AND novelist).

# Initial surefire sparql_table function
# def sparql_table(low, high, *occs):
#     dtmin = str(pd.to_datetime(low, format="%Y").date())
#     dtmax = str(pd.to_datetime(high, format="%Y").date())
#     print(occs)
#     print(type(occs))
#     # literary critic = Q4263842 ; novelist = Q6625963
#     query = f"SELECT DISTINCT ?personLabel ?person ?birth ?article WHERE {{?person wdt:P106 wd:{occs[0]}, wd:{occs[1]}; wdt:P569 ?birth. ?article schema:about ?person; schema:isPartOf <https://en.wikipedia.org/>; schema:inLanguage 'en'. FILTER((?birth > '{dtmin}'^^xsd:dateTime) && (?birth < '{dtmax}'^^xsd:dateTime)) SERVICE wikibase:label {{ bd:serviceParam wikibase:language '[AUTO_LANGUAGE],en'. }}}} ORDER BY (?birth)"
#     resp = S.post(url = qu, params = {'query': query, 'format': 'json'}).text
#     out = json.loads(resp)
#
#     data = {}
#
#     for i in out['results']['bindings'][0].keys():
#         data[i] = []
#
#     for i in out['results']['bindings']:
#         for j in range(len(i.keys())):
#             k = list(i.keys())[j]
#             data[k].append(i[k]['value'])
#
#     table = pd.DataFrame(data)
#     return table
#
# Final entry is only 1985?

# %%
