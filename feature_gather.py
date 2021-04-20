#import os
#os.chdir("C://brain//rutgers//564//wikiproject")

from scrapes import *
from sparql_to_dataframe import *

import pandas as pd
import requests, json

def occ_mask(table):
	po_dict = {}
	occ_list = []
	S = requests.Session()
	p = {
		"action": "wbgetentities",
		"ids": "0",
		"languages": "en",
		"props": "claims",
		"format": "json"
	}
	for i in table.QID:
		p['ids'] = i
		data = S.get(url="https://www.wikidata.org/w/api.php", params=p)
		jdata = json.loads(data.text)
		occl = []
		for j in jdata['entities'][p['ids']]['claims']['P106']:
			qocc = j['mainsnak']['datavalue']['value']['id']
			occl.append(qocc)
			occ_list.append(qocc)
		po_dict[i] = occl

	occu = list(set(occ_list))
	for i in po_dict.keys():
	    table.loc[table.QID == i, occu] = [1 if x in [occu.index(y) for y in po_dict[i]] else 0 for x in range(len(occu))]

	return table

# z = occ_mask(sparql_table(1800, 1900, "Q4263842", "Q6625963"))
# z['text'] = z['personLabel'].apply(get_text)

def cleaner(text):
	text = str(text)
	text = text.replace('\n','')
	text = text.replace('&amp;',' ')
	text = text.replace('&nbsp;','')
	text = text.replace('#x200B;','')
	text = text.replace('*', '')
	text = text.replace('&gt;', '')
	text = str(text)
	text = text.lower()
	return text

# z['textc'] = z.text.apply(cleaner)

# %%
