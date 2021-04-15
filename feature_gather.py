from scrapes import *
from sparql_to_dataframe import *

for i in ppl.QID:
    p['ids'] = i
    data = S.get(url=URL, params=p)
    jdata = json.loads(data.text)
    occl = []
    for j in jdata['entities'][p['ids']]['claims']['P106']:
        qocc = j['mainsnak']['datavalue']['value']['id']
        occl.append(qocc)
        occ_list.append(qocc)
    po_dict[i] = occl

occu = list(set(occ_list))
occs = set(occ_list)
po_dict
list(po_dict.values())
