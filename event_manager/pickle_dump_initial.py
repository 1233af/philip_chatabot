import pickle

DBids = {}


with open('DBids.p', 'wb') as f:
    pickle.dump(DBids, f)