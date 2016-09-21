import nltk.tokenize.punkt as punkt
import glob
import re
import cPickle as pickle
import copy
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

def train_tokenizer():
    trainer = punkt.PunktTrainer()
    trainer.INCLUDE_ALL_COLLOCS = True
    print 'Training the tokenizer on SemEval'
    for semeval_file in semeval_files:
        print 'File', semeval_file
        try:
            with open(semeval_file, 'r') as f:
                st = []
                for line in f:
                    st += [line.strip()]
                text = read_visit_sem(st)
                trainer.train(text, finalize=False)
        except IOError:
            pass
    trainer2 = copy.deepcopy(trainer)
    trainer2.finalize_training()
    tokenizer = punkt.PunktSentenceTokenizer(trainer2.get_params())
    out = open("tokenizer.pk", "wb")
    pickle.dump(tokenizer, out, -1)
    out.close()
    tokenizer = None
    trainer2 = None
    print 'Wrote tokenizer.'
    print 'Training the tokenizer on MIMIC'
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
                        trainer.train(text, finalize=False)
                        st = []
                    elif line.strip() != '<VISIT>':
                        st += [line.strip()]
        except IOError:
            continue
        trainer2 = copy.deepcopy(trainer)
        trainer2.finalize_training()
        tokenizer = punkt.PunktSentenceTokenizer(trainer2.get_params())
        out = open("tokenizer.pk", "wb")
        pickle.dump(tokenizer, out, -1)
        out.close()
        print 'Wrote tokenizer.'

train_tokenizer()
