from __future__ import division

import nltk
import cPickle as pickle

with open('vocab_fd.pk', 'rb') as f:
    fd = pickle.load(f)

vals = sorted(fd.values(), reverse=True)
N = fd.N()

targets = [50., 90., 95., 98., 98.5, 99., 99.5, 99.9, 100.]

tot = 0

for i, v in enumerate(vals, 1):
    tot += v
    if 100. * tot / N >= targets[0]:
        print targets[0], i
        targets.pop(0)
        if not targets:
            break
