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
    sentences += [read_sentence(''.join(y))]
    f.close()
    return sentences
