# This file contains function to read the text version of UMLS, as produced
# by https://github.com/clinicalml/ML-tools/blob/master/UMLS/ProcessUMLS.py

import ast
import marisa_trie
import sys
import cPickle as pickle

from datetime import datetime as time
from nltk.tokenize import word_tokenize as split_tokens

reload(sys)
sys.setdefaultencoding('utf8')

goodtypes = [
    'Congenital Abnormality', 'Acquired Abnormality', 'Injury or Poisoning',
    'Pathologic Function', 'Disease or Syndrome', 'None',
    'Mental or Behavioral Dysfunction', 'Cell or Molecular Dysfunction',
    'Experimental Model of Disease', 'Anatomical Abnormality',
    'Neoplastic Process', 'Sign or Symptom', 'Laboratory or Test Result'
]


# to_str_list reconstructs a list from the output of print
def str_to_list(st):
    return ast.literal_eval(st.strip())


def normalize(st):
    # TODO: normalize descriptions further
    return st


# This function reads a split() line of UMLSlite.dat and returns a list
def remake(UMLSitem):
    res = UMLSitem[:]
    res[2] = int(res[2])
    res[3] = str_to_list(res[3])
    res[4] = list(set([normalize(st) for st in str_to_list(res[4])]))
    return res


# This function check whether the concept is of the right type
def good_type_list(UMLSitem):
    ls1 = UMLSitem[3]
    res = []
    for tp in ls1:
        if tp in goodtypes:
            res += [tp]
    return res


# This function helps build a lookup table from string description to
# concepts
def auxUMLS(UMLSitem, lookup):
    for st in UMLSitem[4]:
        lookup[st] = lookup.get(st, []) + [UMLSitem[2]]


# This function reads a text formatted version of UMLS, and returns
# a list of entries, a lookup table, and a prefix tree
def read_umls(UMLSfile):
    print time.now(), '\t', "Reading", UMLSfile
    try:
        UMLS, lookup, trie, prefix_trie, suffix_trie, spelling_trie, acro_trie = pickle.load(open('UMLSprocessed.pk'))
    except:
        f = open(UMLSfile)
        preUMLS = [(line.strip() + ' ').split(' |||| ')[:-1] for line in f]
        f.close()
        print time.now(), '\t', "Read UMLS"
        UMLS = map(remake, preUMLS[1:])
        print time.now(), '\t', "Loaded UMLS"
        UMLSrest = filter(lambda x: len(good_type_list(x)) > 0, UMLS)
        # Prefix trees
        fmt = "<i"
        # Regular
        data = []
        for i, concept in enumerate(UMLSrest):
            i = int(concept[0][1:]) if concept[0].lower() != "cui-less" else 0
            for st in concept[4]:
                data.append((unicode(st), (i,)))
        trie = marisa_trie.RecordTrie(fmt, data)
        # Suffixes
        data = []
        for i, concept in enumerate(UMLSrest):
            i = int(concept[0][1:]) if concept[0].lower() != "cui-less" else 0
            for st in concept[4]:
                q = st.split()
                for j in range(len(q) - 3):
                    new_st = u" ".join(q[j:])
                    data.append((unicode(new_st), (i,)))
        suffix_trie = marisa_trie.RecordTrie(fmt, data)
        # Prefixes
        data = []
        for i, concept in enumerate(UMLSrest):
            i = int(concept[0][1:]) if concept[0].lower() != "cui-less" else 0
            for st in concept[4]:
                q = st.split()
                for j in range(3, len(q)):
                    new_st = u" ".join(q[:j])
                    data.append((unicode(new_st), (i,)))
        prefix_trie = marisa_trie.RecordTrie(fmt, data)
        # Word prefixes
        data = []
        for i, concept in enumerate(UMLSrest):
            i = int(concept[0][1:]) if concept[0].lower() != "cui-less" else 0
            for st in concept[4]:
                if len(st.split()) == 1:
                    data.append((unicode(st), (i,)))
        spelling_trie = marisa_trie.RecordTrie(fmt, data)
        # Acronyms
        data = []
        for i, concept in enumerate(UMLSrest):
            i = int(concept[0][1:]) if concept[0].lower() != "cui-less" else 0
            for st in concept[4]:
                q = [unicode(w) for w in st.split()]
                if len(q) <= 1:
                    continue
                acro = [w[0] for w in q]
                data.append((u"".join(acro), (i,)))
                data.append((u"%s %s" % (q[0], "".join(acro[1:])), (i,)))
                data.append((u"%s %s" % ("".join(acro[:-1]), q[-1]), (i,)))
        acro_trie = marisa_trie.RecordTrie(fmt, data)
        print time.now(), '\t', "Made trie"
        lookup = {}
        foo = map(lambda x: auxUMLS(x, lookup), UMLS)
        print time.now(), '\t', "Made lookup"
        pickle.dump((UMLS, lookup, trie, prefix_trie, suffix_trie,
                     spelling_trie, acro_trie), open('UMLSprocessed.pk', 'w'))
    print time.now(), '\t', "Processed UMLS"
    return UMLS, lookup, trie, prefix_trie, suffix_trie, \
        spelling_trie, acro_trie
