from gensim.models import Phrases
import nltk
import glob
import re
import cPickle as pickle
import os.path
import random

mimic_dir = '/data/ml2/jernite/MIMIC3/Parsed/MIMIC3_split'
#mimic_dir = '/home/ankit/devel/data/MIMIC3_split'
mimic_dirs = glob.glob(mimic_dir + r'/[0-9]*')
notes_files = [d + '/NOTEEVENTS_DATA_TABLE.csv' for d in mimic_dirs]
notes_files = [f for f in notes_files if os.path.isfile(f)]

semeval_dir = '/data/ml2/ankit/semeval_data'
#semeval_dir = '/home/ankit/devel/data/data'
semeval_dirs = glob.glob(semeval_dir + r'/*')
semeval_files = sum([glob.glob(d + r'/*.text') for d in semeval_dirs], [])

re_anon = re.compile(r'ANON__.*?__ANON')
re_sem = re.compile(r'\[\*\*.*?\*\*\]')

def treat_line(line):
    return re_anon.sub('<unk>', line)

def treat_line_sem(line):
    return re_sem.sub('<unk>', line)

def read_visit(lines):
    return treat_line(' '.join(lines[1:]))

def read_visit_sem(lines):
    return treat_line_sem(' '.join(lines[1:]))

def subset(seq, k):
    if not 0<=k<=len(seq):
        for e in seq:
            yield e
    else:
        numbersPicked = 0
        for i,number in enumerate(seq):
            prob = (k-numbersPicked)/(len(seq)-i)
            if random.random() < prob:
                yield number
                numbersPicked += 1

def next_note(tokenizer):
    print 'SemEval data'
    for semeval_file in semeval_files:
        print 'File', semeval_file
        with open(semeval_file, 'r') as f:
            st = []
            for line in f:
                st += [line.strip()]
            text = read_visit_sem(st)
            text = tokenizer.tokenize(text)
            for sent in text:
                yield nltk.word_tokenize(sent.lower())
    print 'MIMIC data'
    for notes_file in subset(notes_files, 15): # 15 random MIMIC files
        print 'File', notes_file
        try:
            with open(notes_file, 'r') as f:
                ct = 0
                st = []
                for line in f:
                    ct += 1
                    if ct % 50000 == 0:
                        print ct
                    if line.strip() == '</VISIT>':
                        text = read_visit(st)
                        text = tokenizer.tokenize(text)
                        for sent in text:
                            yield nltk.word_tokenize(sent.lower())
                        st = []
                    elif line.strip() != '<VISIT>':
                        st += [line.strip()]
        except IOError:
            pass

f = open("tokenizer.pk", "rb")
tokenizer = pickle.load(f)
f.close()

print 'BIGRAMS'
bigram = Phrases(next_note(tokenizer), delimiter='')
bigram.save('bigrams.pk')

print 'TRIGRAMS'
trigram = Phrases(bigram[next_note(tokenizer)], delimiter='')
trigram.save('trigrams.pk')

print '4GRAMS'
ngram = Phrases(trigram[next_note(tokenizer)], delimiter='')
ngram.save('ngrams.pk')

