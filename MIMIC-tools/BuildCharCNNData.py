import glob
import nltk
import os.path
import random
import cPickle as pickle
import re
from multiprocessing import Pool

from mimictools import utils

train_size = 15
valid_size = 5
test_size = 8

vocab_size = 15000

mimic_dir = '/data/ml2/jernite/MIMIC3/Parsed/MIMIC3_split'
#mimic_dir = '/home/ankit/devel/data/MIMIC3_split'
mimic_dirs = sorted(glob.glob(mimic_dir + r'/[0-9]*'))
notes_files = [d + '/NOTEEVENTS_DATA_TABLE.csv' for d in mimic_dirs]
notes_files = [f for f in utils.subset([f for f in notes_files
                                              if os.path.isfile(f)],
                                        train_size + valid_size + test_size)]
random.shuffle(notes_files)

fix_re = re.compile(r"[^a-z0-9/'?.,-]+")
num_re = re.compile(r'[0-9]+')
dash_re = re.compile(r'-+')

def fix_word(word):
    word = word.lower()
    word = fix_re.sub('-', word).strip('-')
    word = num_re.sub('#', word)
    word = dash_re.sub('-', word)
    return word

files = {}
files['train'] = notes_files[:train_size]
notes_files = notes_files[train_size:]
files['valid'] = notes_files[:valid_size]
files['test'] = notes_files[valid_size:]

with open('vocab_fd.pk', 'rb') as f:
    vocab_fd = pickle.load(f)
vocab = set(k for k,v in vocab_fd.most_common(25000))

def prepare_dataset(out):
    with open(out + '.txt', 'w') as f:
        for _, raw_text in utils.mimic_data(files[out], replace_anon='//unk//',
                                            verbose=True):
            sentences = nltk.sent_tokenize(raw_text)
            for sent in sentences:
                words = [fix_word(w) for w in nltk.word_tokenize(sent)
                                        if any(c.isalpha() or c.isdigit()
                                            for c in w)]
                finalwords = []
                for word in words:
                    if not word: continue
                    if word in vocab:
                        finalwords.append(word)
                    else:
                        finalwords.append('<unk>')
                line = ' '.join(finalwords)
                if line:
                    print >> f, ' ' + line.replace('//unk//', '<unk>')

p = Pool(3)
p.map(prepare_dataset, ['train', 'valid', 'test'])
