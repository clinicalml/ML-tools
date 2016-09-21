from gensim.models import Phrases
import nltk
import glob
import re
import cPickle as pickle
import os.path
import random

#semeval_dir = '/data/ml2/ankit/semeval_data'
semeval_dir = '/home/ankit/devel/data/data'
semeval_dirs = [semeval_dir + '/train', semeval_dir + '/dev']
semeval_files = sum([glob.glob(d + r'/*.text') for d in semeval_dirs], [])

re_sem = re.compile(r'\[\*\*.*?\*\*\]')

def treat_line_sem(line):
    return re_sem.sub('<unk>', line)

def read_visit_sem(lines):
    return treat_line_sem(' '.join(lines[1:]))

f = open("tokenizer.pk", "rb")
tokenizer = pickle.load(f)
f.close()

bigram = Phrases.load('bigrams.pk')
trigram = Phrases.load('trigrams.pk')
ngram = Phrases.load('ngrams.pk')

print 'SemEval data'
for semeval_file in semeval_files:
    print 'File', semeval_file
    with open(semeval_file, 'r') as f:
        st = []
        for line in f:
            st += [line.strip()]
        text = read_visit_sem(st)
        text = [nltk.word_tokenize(s.lower()) for s in tokenizer.tokenize(text)]
        text = ngram[trigram[bigram[text]]]
        for sent in text:
            print '->', ' '.join(sent)
        print '==='
        print

