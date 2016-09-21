import glob
import nltk
from nltk.corpus import stopwords
import os.path
import cPickle as pickle
import multiprocessing
from multiprocessing import Pool

from mimictools import utils

mimic_dir = '/data/ml2/jernite/MIMIC3/Parsed/MIMIC3_split'
#mimic_dir = '/home/ankit/devel/data/MIMIC3_split'
mimic_dirs = sorted(glob.glob(mimic_dir + r'/[0-9]*'))
notes_files = [d + '/NOTEEVENTS_DATA_TABLE.csv' for d in mimic_dirs]
notes_files = [f for f in notes_files if os.path.isfile(f)]

stop = set(str(s) for s in stopwords.words('english'))
stop.add('unk')

def filt(ngrams):
    for ng in ngrams:
        skip = False
        for t in ng:
            if t in stop or not any(c.isalpha() for c in t):
                skip = True
                break
        if not skip:
            yield ng

def get_stats(notes_file):
    unigram_fd = nltk.FreqDist()
    bigram_fd = nltk.FreqDist()
    trigram_fd = nltk.FreqDist()
    qgram_fd = nltk.FreqDist()
    for _, raw_text in utils.mimic_data([notes_file], super_verbose=True):
        sentences = nltk.sent_tokenize(raw_text)
        for sent in sentences:
            words = [w.lower() for w in nltk.word_tokenize(sent)]
            unigram_fd.update(filt(nltk.ngrams(words, 1)))
            bigram_fd.update(filt(nltk.ngrams(words, 2)))
            trigram_fd.update(filt(nltk.ngrams(words, 3)))
            qgram_fd.update(filt(nltk.ngrams(words, 4)))
    return (unigram_fd, bigram_fd, trigram_fd, qgram_fd)

p = Pool(int(.5 + (.9 * float(multiprocessing.cpu_count()))))
stats = p.map(get_stats, notes_files)

print 'Got the stats.'

unigram_fd = nltk.FreqDist()
bigram_fd = nltk.FreqDist()
trigram_fd = nltk.FreqDist()
qgram_fd = nltk.FreqDist()

for u, b, t, q in stats:
    unigram_fd.update(u)
    bigram_fd.update(b)
    trigram_fd.update(t)
    qgram_fd.update(q)

def print_common(fd, k):
    for i, (ng, count) in enumerate(fd.most_common(k)):
        print i+1, '\t'+' '.join(ng), '\t('+str(count)+')'
    print

print '\nUnigrams'
print_common(unigram_fd, 50)
print 'Bigrams'
print_common(bigram_fd, 50)
print 'Trigrams'
print_common(trigram_fd, 50)
print '4-grams'
print_common(qgram_fd, 50)

print 'Saving stats.'
with open('ngrams.pk', 'wb') as f:
    pickle.dump((unigram_fd, bigram_fd, trigram_fd, qgram_fd), f, -1)
print 'Done.'
