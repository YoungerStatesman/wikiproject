import os
os.getcwd()
os.chdir("C://brain//rutgers//564//wikiproject")

#################################################
#                                               #
#  IMPORTANT: store sparql_table output as "z"  #
#                                               #
#################################################

from scrapes import *
from sparql_to_dataframe import *
from feature_gather import *
import re
from sklearn.feature_extraction.text import CountVectorizer as cv
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn import metrics
from nltk.corpus import stopwords
stoplist = stopwords.words('english')

def nostops(text):
	clean = [word for word in text.split() if word not in stoplist]
	return clean

#######################################################
#                                                     #
#          place for a SPARQL/session call            #
z = pd.read_json('table_18001900_occandtext.json')    #
#                                                     #
#######################################################

# %% Identifying the location of the first occupational QID column for filtering.

qcol = []
for i in z.columns:
	if re.search(r"Q\d+", i):
		qcol.append(i)

firstq = z.columns.get_loc(qcol[0])

# Reducing the dataframe to only occupational labels occurring more than 5 times.

tofilter = z.iloc[:, firstq:]
over5 = tofilter.iloc[:, (z.iloc[:, firstq:].sum() > 5).values].columns
z = z.loc[:, z.columns[:firstq].append(over5)]

# A list of all occupational QID columns

qcol = []
for i in z.columns:
	if re.search(r"Q\d+", i):
		qcol.append(i)

# Text cleaning

z['text'] = z['text'].apply(nostops).apply(lambda i: ' '.join(i)).apply(cleaner)
z.insert(z.columns.get_loc(qcol[0]), 'sets', z['text'].apply(lambda i: set(re.findall("[a-z]{3,}", i))))
z['sets'] = [([a for a in x if a not in stoplist]) for x in z['sets']]
z['sets'] = list(map(set, z['sets']))
z['sets'] = z.sets.apply(lambda i: ' '.join(i))

# %% Naive Bayes loop function

# Using "0.0"/"1.0" or "0"/"1"? Poorly defined in feature_gather.py maybe?

def bayes(frame, size):
	vec = cv(stop_words='english', max_features=30000);
	vec.fit(frame.sets)
	X = vec.transform(frame.text).toarray()
	acc = []; rec = []; pre = []; cts = []; totalcts = []; cm = []; label_used = []; auc = [];
	for i in qcol:
		X_train, X_test, y_train, y_test = train_test_split(X, frame.loc[:, i], test_size=size, random_state=0)
		gb = GaussianNB()
		gb.fit(X_train, y_train)
		pred = gb.predict(X_test)
		try:
			output = metrics.classification_report(y_test, pred, output_dict=True, zero_division=0)['0']
			auc_score = metrics.roc_auc_score(y_test, pred)
			a = 0
		except:
			output = metrics.classification_report(y_test, pred, output_dict=True, zero_division=0)['1']
			a = 1
			auc_score = 'N/A'

		label_used.append(str(a))
		acc.append("{:0.3}".format(metrics.accuracy_score(y_test, pred)))
		pre.append("{:0.3}".format(output['precision']))
		rec.append("{:0.3}".format(output['recall']))
		cts.append(y_test.sum())
		cm.append(metrics.confusion_matrix(y_test, pred))
		auc.append(auc_score)
		totalcts.append(sum(frame.loc[:, i]))
		# print(i, output)

	d = {'label': label_used, 'acc': acc, 'pre': pre, 'rec': rec, 'auc': auc, 'cts': cts, 'totalcts': totalcts, 'conf': cm}
	df = pd.DataFrame(data=d, index=qcol)
	return df

bayes(z, .25)
