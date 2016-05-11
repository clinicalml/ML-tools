# reads the CRF output


def propose_cuis(men, UMLS, lookup):
    if men.lower() in lookup:
        return ' '.join([UMLS[idx][0] for idx in lookup[men.lower()]])
    else:
        return 'NOT_FOUND'


def tags_to_mentions(tagging):
    rebuild = []
    core = []
    added = []
    for i, tag in enumerate(tagging):
        if tag == 'Bp':
            if len(core) > 0:
                if len(added) <= 1:
                    added += [[]]
                for a in added:
                        rebuild += [sorted(a[:] + core[:])]
                core = []
                added = []
            added += [[i]]
        if tag in ['In', 'IDn']:
            added += [[i]]
        if tag in ['Ip', 'IDp']:
            if len(added) == 0:
                added += [[i]]
                print 'BUG', tagging
            else:
                added[-1] += [i]
        if tag in ['B', 'O'] and len(core) > 0:
            if len(added) <= 1:
                added += [[]]
            for a in added:
                    rebuild += [sorted(a[:] + core[:])]
            core = []
            added = []
        if tag in ['B', 'I', 'ID']:
            core += [i]
    if len(core) > 0:
        if len(added) <= 1:
            added += [[]]
        for a in added:
                rebuild += [sorted(a[:] + core[:])]
    return sorted([tuple(x) for x in rebuild])


def read_sentence(y):
    sentence = y.splitlines()[1:]
    tags = [(token.split()[-10], token.split()[-9].split('/')[0], token.split()[-8:])
            for token in sentence if len(token) > 0]
    text = [token.split()[0] for token in sentence if len(token) > 0]
    pre_found = tags_to_mentions([tag[1] for tag in tags])
    found = [(x, ' '.join(text[i] for i in x)) for x in pre_found]
    return [' '.join(text), found]


def treat_sentences(results_file):
    sentences = []
    ct = 0
    f = open(results_file)
    y = []
    for line in f:
        if line.startswith('# '):
            if len(y) > 0:
                ct += 1
                sentences += [read_sentence(''.join(y))]
            y = [line]
        else:
            y = y + [line]

    sentence = read_sentence(''.join(y))
    words = sentence[0].split('')
    identified_concepts = sentence[1]
    pos, neg = concepts_list(words, identified_concepts)
    sentences += [(sentence[0], pos, neg)]  
    f.close()
    return sentences




fullstops=['.', '-', ';']
midstops=['+', 'but', 'and', 'pt', 'except', 'reports', 'alert',
          'complains', 'has', 'states', 'secondary', 'per', 'did', 'aox3']

negwords=['no', 'not', 'denies', 'without', 'non']

# Returns list of negation scopes.
# Exple: ['Patient', 'presents', 'no', 'sign', 'of', 'fever', 'but', 'complains', 'of', 'headaches']
# Result: [(2, 5)]
def annotate(words, max_span_length=20):
    flag = 0
    res = []
    count_words = 0
    for i, w in enumerate(words):
        count_words += 1
        neg_start_condition = (flag == 1)
        neg_stop_condition =  (w in fullstops + midstops + negwords) or \
                              (count_words == max_span_length)
        # corner case of end of list without stops
        neg_end_of_list = (i == (len(words) - 1))
        if neg_start_condition and neg_stop_condition:
            flag = 0
            res += [(start_index, i - 1)]
        elif neg_start_condition and neg_end_of_list:
            flag = 0
            res += [(start_index, i)]
        if w in negwords:
            flag = 1
            start_index = i
            count_words = 0
    return res


#########
## Combine the two
##########

# returns list of positive UMLS matches and negative UMLS matches
def concepts_list(words, identified_concepts):
    #concepts = find_concepts(words, trie, lookup)
    negations = annotate(words)
    positive = []
    negative = []
    for co in identified_concepts:
        negated = False
        for span in negations:
            concept_begins = co[0][0]
            concept_ends = co[0][-1]
            if span[0] < concept_begins and concept_ends <= span[1]:
                negated = True
        if negated:
            negative += [co]
        else:
            positive += [co]
    return (positive, negative)
