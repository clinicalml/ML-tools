############
## Trie matches
############
import ast
import sys
import cPickle as pickle

import marisa_trie

from string import punctuation as punct


reload(sys)
sys.setdefaultencoding('utf8')

goodtypes = [
    'Congenital Abnormality', 'Acquired Abnormality', 'Injury or Poisoning',
    'Pathologic Function', 'Disease or Syndrome', 'None',
    'Mental or Behavioral Dysfunction', 'Cell or Molecular Dysfunction',
    'Experimental Model of Disease', 'Anatomical Abnormality',
    'Neoplastic Process', 'Sign or Symptom', 'Laboratory or Test Result', 'Finding'
]

UMLSfile = 'UMLStok.dat'


# This function reads a split() line of UMLSlite.dat and returns a list
def remake(UMLSitem):
    res = UMLSitem[:]
    res[2] = int(res[2])
    res[3] = ast.literal_eval(res[3])
    res[4] = list(set([st for st in ast.literal_eval(res[4])]))
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


# Reads a processed version of UMLS and 
def read_umls(UMLSfile, google_concepts_list):
    try:
        desc, UMLS = pickle.load(open('UMLSlite.pk'))
    except:
        f = open(UMLSfile)
        preUMLS = [(line.strip() + ' ').split(' |||| ')[:-1] for line in f]
        f.close()
        print "Read UMLS"
        UMLS = map(remake, preUMLS[1:])
        pickle.dump((preUMLS[0], UMLS), open('UMLSlite.pk', 'w'))
    print "Loaded UMLS"
    UMLSrest = filter(lambda x: len(good_type_list(x)) > 0, UMLS)
    # Prefix trees
    fmt = "<i"
    # Regular
    data = []
    lookup = {}
    for i, concept in enumerate(UMLSrest):
        i = int(concept[0][1:]) if concept[0].lower() != "cui-less" else 0
        for st in concept[4]:
            data.append((unicode(st), (i,)))
    for i, (mid, descriptions) in enumerate(google_concepts_list):
        for st in descriptions:
            data.append((unicode(st), (len(UMLSrest) + i,)))
            lookup[st] = lookup.get(st, []) + [mid]
    trie = marisa_trie.RecordTrie(fmt, data)
    print "Made trie"
    foo = map(lambda x: auxUMLS(x, lookup), UMLS)
    print "Made lookup"
    return UMLS, lookup, trie


#UMLS, lookup, trie = read_umls(UMLSfile, [])


def remove_sub_strings(match_list):
    res = []
    for (match, cuis, start, ending) in match_list:
        sub_string = False
        for (match_1, cuis_1, start_1, ending_1) in res:
            if start_1 <= start and ending_1 >= ending:
                sub_string = True
        if not sub_string:
            res += [(match, cuis, start, ending)]
    return res


# words is a list of words
def find_concepts(words, trie, lookup):
    note_text = unicode(' '.join(words))
    idx = 0
    res = []
    for i in range(len(note_text)):
        if note_text[i] == ' ':
            idx += 1
        if i == 0 or note_text[i-1] in punct + ' ':
            matches = trie.prefixes(note_text[i:i + 150])
            if len(matches) == 0:
                continue
            else:
                l_matches = map(len, matches)
                match = matches[l_matches.index(max(l_matches))]
                if len(match) > 3:
                    res += [(match, lookup[match], idx, idx + len(match.split()) - 1)]
    return remove_sub_strings(res)


############
## Negation detection
############


fullstops=['.', '-', ';']
midstops=['+', 'but', 'and', 'pt', 'except', 'reports', 'alert', 'complains', 'has', 'states', 'secondary', 'per', 'did', 'aox3']
    
negwords=['no', 'not', 'denies', 'without', 'non']

## returns list of scopes and annotated sentence.
#Exple: Patient presents no sign of fever but complains of headaches
# Result: [(2, 5)]
def annotate(words):
    flag = 0
    res = []
    for i, w in enumerate(words):
        neg_start_condition = (flag == 1)
        neg_stop_condition =  (w in fullstops + midstops + negwords)
        # corner case of end of list without stops
        neg_end_of_list = (i==(len(words)-1) )

        if neg_start_condition and neg_stop_condition:
            flag = 0
            res += [(start_index, i-1)]

        elif neg_start_condition and neg_end_of_list:
            flag = 0
            res += [(start_index, i)]
            
        if w in negwords:
            flag = 1
            start_index = i
    return res



##########
## Combine the two
##########

def concepts_list(words, trie, lookup):
    concepts = find_concepts(words, trie, lookup)
    negations = annotate(words)
    positive = []
    negative = []
    for co in concepts:
        negated = False
        for span in negations:
            concept_begins = co[2]
            concept_ends = co[3]
            if span[0] < concept_begins and concept_ends <= span[1]:
                negated = True
        if negated:
            negative += [co]
        else:
            positive += [co]
    return (positive, negative)




