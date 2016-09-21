from __future__ import division

import nltk
import cPickle as pickle

alpha = 0.5

print 'Loading ngrams'
with open('ngrams.pk', 'rb') as f:
    ngrams = list(pickle.load(f))
print 'Loaded.'

print 'Merging dists'
merged = nltk.FreqDist()
for fd in ngrams:
    merged.update(fd)
print 'Merged.'

print 'Computing scores'
for i in range(1, len(ngrams)):
    print i+1, 'grams'
    fd = ngrams[i]
    newfd = nltk.FreqDist()
    for ng, count in fd.items():
        scores = []
        for split in range(1, i+1):
            token1 = ng[:split]
            token2 = ng[split:]
            cur_score = count**(2+alpha) / (merged[token1] * merged[token2])
            scores.append(cur_score)
        newfd[ng] = sum(scores) / len(scores)
    ngrams[i] = newfd
print 'Done.'

def print_common(fd, k):
    for i, (ng, count) in enumerate(fd.most_common(k)):
        print i+1, '\t'+' '.join(ng), '\t('+str(count)+')'
    print

for n in range(len(ngrams)):
    print n+1, 'grams'
    print_common(ngrams[n], 100)

print 'Saving'
with open('ngrams_scored.pk', 'wb') as f:
    pickle.dump(ngrams, f, -1)
print 'Saved.'
