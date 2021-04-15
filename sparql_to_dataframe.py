from scrapes import *

# Test of imported functions
# THESE ALL WORK! HOORAY!!!
# Q170509 = Henry James (Example)

safename("https://en.wikipedia.org/wiki/James Joyce")
countWords("The rain in Spain stays mainly in the plain.")
get_label("Q170509")
countWords(get_text(get_label('Q170509')))

# %%
# Outputs dataframe based on the input range for birth dates (e.g. 1800-1900)
# and the occupation labels, in this case literary critic AND novelist.

def sparql_table(low, high):
    dtmin = str(pd.to_datetime(low, format="%Y").date())
    dtmax = str(pd.to_datetime(high, format="%Y").date())
    # literary critic = Q4263842 ; novelist = Q6625963
    query = f"SELECT DISTINCT ?personLabel ?person ?birth ?article WHERE {{?person wdt:P106 wd:Q4263842, wd:Q6625963; wdt:P569 ?birth. ?article schema:about ?person; schema:isPartOf <https://en.wikipedia.org/>; schema:inLanguage 'en'. FILTER((?birth > '{dtmin}'^^xsd:dateTime) && (?birth < '{dtmax}'^^xsd:dateTime)) SERVICE wikibase:label {{ bd:serviceParam wikibase:language '[AUTO_LANGUAGE],en'. }}}} ORDER BY (?birth)"
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
    return table
