import glob
import nltk
from nltk.corpus import stopwords
import os.path
import cPickle as pickle
import re
import multiprocessing
from multiprocessing import Pool

from mimictools import utils

mimic_dir = '/data/ml2/jernite/MIMIC3/Parsed/MIMIC3_split'
#mimic_dir = '/home/ankit/devel/data/MIMIC3_split'
mimic_dirs = sorted(glob.glob(mimic_dir + r'/[0-9]*'))
notes_files = [d + '/NOTEEVENTS_DATA_TABLE.csv' for d in mimic_dirs]
notes_files = [f for f in notes_files if os.path.isfile(f)]

fix_re = re.compile(r"[^a-z0-9/'?.,-]+")
num_re = re.compile(r'[0-9]+')
dash_re = re.compile(r'-+')

def fix_word(word):
    word = word.lower()
    word = fix_re.sub('-', word).strip('-')
    word = num_re.sub('#', word)
    word = dash_re.sub('-', word)
    return word

def process_notes(notes_file):
    all_words = []
    for _, raw_text in utils.mimic_data([notes_file], replace_anon='_',
                                        verbose=True):
        sentences = nltk.sent_tokenize(raw_text)
        words = [fix_word(w) for sent in sentences
                             for w in nltk.word_tokenize(sent)
                                 if any(c.isalpha() or c.isdigit() for c in w)]
        all_words.extend(w for w in words if w)
    return nltk.FreqDist(all_words)

p = Pool(int(.5 + (.9 * float(multiprocessing.cpu_count()))))
outs = p.map(process_notes, notes_files)
fd = nltk.FreqDist()
for fdi in outs:
    fd.update(fdi)
print
print 'FINAL'
print 'Top 100:', fd.most_common(100)
print 'Vocab size:', fd.B()
print 'Writing FD ...',
try:
    with open('vocab_fd.pk', 'wb') as f:
        pickle.dump(fd, f, -1)
        print 'Done.'
except IOError:
    print 'Failed'
