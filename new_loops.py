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

# %% To create a dataframe ready for the bayes function:
# z = occ_mask(sparql_table(1800, 1900, "Q4263842", "Q6625963"))
# z.insert(5, 'text', z['personLabel'].apply(get_text))

# %% Identifying the location of the first occupational QID column for filtering.

def getqcols(frame):
	qcol = []
	for i in frame.columns:
		if re.search(r"Q\d+", i):
			qcol.append(i)
	return qcol

# %% Naive Bayes loop function

# Using "0.0"/"1.0" or "0"/"1"? Poorly defined in feature_gather.py maybe?

def bayes(frame, size, occmin):

	# Filtering dataset to occupations over n
	unfiltq = getqcols(frame)
	firstq = frame.columns.get_loc(unfiltq[0])
	tofilter = frame.iloc[:, firstq:]
	overmin = tofilter.iloc[:, (frame.iloc[:, firstq:].sum() > occmin).values].columns
	frame = frame.loc[:, frame.columns[:firstq].append(overmin)]

	filtq = getqcols(frame)
	firstq = frame.columns.get_loc(filtq[0])

	# Text cleaning
	frame['text'] = frame['text'].apply(nostops).apply(lambda i: ' '.join(i)).apply(cleaner)
	frame.insert(frame.columns.get_loc(filtq[0]), 'sets', frame['text'].apply(lambda i: set(re.findall("[a-z]{3,}", i))))
	frame['sets'] = [([a for a in x if a not in stoplist]) for x in frame['sets']]
	frame['sets'] = list(map(set, frame['sets']))
	frame['sets'] = frame.sets.apply(lambda i: ' '.join(i))

	# Vectorizer, fit, df data
	vec = cv(stop_words='english', max_features=30000);
	vec.fit(frame.sets)
	X = vec.transform(frame.text).toarray()
	acc = []; rec = []; pre = []; cts = []; totalcts = []; cm = []; label_used = []; auc = [];

	# Bayes loops
	for i in filtq:
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

	d = {'label': label_used, 'acc': acc, 'pre': pre, 'rec': rec, 'auc': auc, 'cts': cts, 'totalcts': totalcts, 'conf': cm}
	df = pd.DataFrame(data=d, index=filtq)
	return df
