from __future__ import division

import cPickle as pickle
import collections

import numpy as np
import matplotlib.pyplot as plt

def dd2():
    return collections.defaultdict(int)

def dd1():
    return collections.defaultdict(dd2)

print 'Loading CFD'
with open('cfd.pk', 'rb') as f:
    cfd = pickle.load(f)
print 'Loaded'

cfd2 = {}

print 'Converting'
for k1,v1 in cfd.items():
    counts = {}
    for k2,v2 in v1.items():
        for k3,v3 in v2.items():
            c = counts.get(k3, 0)
            counts[k3] = c + v3
    cfd2[k1] = counts

print 'Writing new CFD'
with open('aux_cfd.pk', 'wb') as f:
    pickle.dump(cfd2, f, -1)
print 'Done'
