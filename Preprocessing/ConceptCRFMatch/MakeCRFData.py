import re
import argparse
import numpy as np

from string import punctuation as punct

from ReadUMLS import *
from StanNLPInterface import *

UMLS = {}
lookup = {}
trie = []
prefix_trie = []
suffix_trie = []
spelling_trie = []
acro_trie = {}


features = ['word', 'lemma', 'pos', 'normal', 'word_length',
            'prefix', 'suffix', 'all_caps', 'capitalized', 'word_pos',
            'sentence_pos', 'sentence_length', 'med_prefix',
            'umls_match_tag_full', 'umls_match_tag_prefix',
            'umls_match_tag_acro']


# Checks whether words that do not appear in UMLS have a common prefix
# of length >= 5 with a umls word
# (for example: 'angioplasty', 'angiopathy' -> 'angiop')
def find_word_prefixes(tokens, spelling_trie):
    word_prefix = ['' for j in tokens]
    for i, w in enumerate(tokens):
        if len(w) > 4:
            for j in range(max(len(w), 30), 4, -1):
                if word_prefix[i] == '':
                    build = unicode(w[:j])
                    word_prefs = spelling_trie.items(build)
                    if len(word_prefs) > 0:
                        word_prefix[i] = w[:j]
    return word_prefix


# This function normalizes tokens, by collapsing digits and hyphens,
# and removing non-standard characters
def clean_token(token):
    token = re.sub(r"[0-9]{1,}", "0", token)
    token = re.sub(r"-{1,}", "-", token)
    token = re.sub(r"[^A-Za-z0-9,:\-()\'\.]", "[unk]", token)
    token = re.sub(r"(\[unk\]){1,}", "[unk]", token)
    return token.lower()


# This function returns a dictionary of the features extracted from a token:
# POS tag, lemma, prefix, suffix, etc...
def token_features(token):
    res = {}
    word = token['word']
    res['word'] = word
    res['lemma'] = token['lemma']
    res['pos'] = token['POS']
    res['normal'] = clean_token(word)
    res['word_length'] = min(len(word)/2, 5)
    res['prefix'] = word[:3]
    res['suffix'] = word[-3:]
    res['all_caps'] = 0 if word.islower() else 1
    res['capitalized'] = 0 if word[0].islower() else 1
    return res


# This function tags (BIO scheme) sub-strings of a sentence which
# correspond to the description of a concept in UMLS, the first few words
# of such a description, or an acronym of a description
def find_concepts(words, trie, prefix_trie, acro_trie):
    st_note = unicode(' '.join(words))
    full_matches = ['O' for word in words]
    prefix_matches = ['O' for word in words]
    acro_matches = ['O' for word in words]
    idx = 0
    for i in range(len(st_note)):
        if st_note[i] == ' ':
            idx += 1
        if i == 0 or st_note[i-1] in punct + ' ':
            matches = trie.prefixes(st_note[i:i + 150])
            pre_matches = prefix_trie.prefixes(st_note[i:i + 150])
            ac_matches = acro_trie.prefixes(st_note[i:i + 150])
            if len(matches) == 0:
                continue
            else:
                l_matches = map(len, matches)
                match = matches[l_matches.index(max(l_matches))]
                if len(match) > 4:
                    full_matches[idx] = 'B'
                    for j in range(1, len(match.split())):
                        full_matches[idx + j] = 'I'
            if len(pre_matches) == 0:
                continue
            else:
                l_pre_matches = map(len, pre_matches)
                match = pre_matches[l_pre_matches.index(max(l_pre_matches))]
                if len(match) > 4:
                    prefix_matches[idx] = 'B'
                    for j in range(1, len(match.split())):
                        prefix_matches[idx + j] = 'I'
            if len(ac_matches) == 0:
                continue
            else:
                l_ac_matches = map(len, ac_matches)
                match = ac_matches[l_ac_matches.index(max(l_ac_matches))]
                if len(match) > 3:
                    acro_matches[idx] = 'B'
                    for j in range(1, len(match.split())):
                        acro_matches[idx + j] = 'I'
    return full_matches, prefix_matches, acro_matches


# This function extracts features from the output of the StanfordNLP tool
# and returns a list of (words, spans, features) for each sentence in a note
def extract_features(note, trie, prefix_trie, acro_trie, spelling_trie):
    sentences = []
    note_id = note[0]
    for i, sent in enumerate(note[1]):
        # we first extract the features
        words = [token['word'].lower() for token in sent]
        spans = [(int(token['CharacterOffsetBegin']),
                  int(token['CharacterOffsetEnd']))
                 for token in sent]
        med_prefix = find_word_prefixes(words, spelling_trie)
        full_matches, prefix_matches, acro_matches = \
            find_concepts(words, trie, prefix_trie, acro_trie)
        features = [token_features(token) for token in sent]
        for j in range(len(features)):
            features[j]['word_pos'] = min(j / 3, 10)
            features[j]['sentence_pos'] = min(i / 10, 5)
            features[j]['sentence_length'] = min(len(features) / 4, 5)
            features[j]['med_prefix'] = med_prefix[j]
            features[j]['umls_match_tag_full'] = full_matches[j]
            features[j]['umls_match_tag_prefix'] = prefix_matches[j]
            features[j]['umls_match_tag_acro'] = acro_matches[j]
        sentence = (words, spans, features)
        sentences += [sentence]
    return (note_id, sentences)


# writes crfpp formatted data and spans file
def write_crfpp_data(note_id, sentences, text_file, spans_file):
    o = open(text_file, "a")
    s = open(spans_file, "a")
    for sentence in sentences:
        words = sentence[0]
        spans = sentence[1]
        tokens = sentence[2]
        for j, token in enumerate(tokens):
            print >>o, "\t".join([str(token[f]).encode('utf-8')
                                  if len(str(token[f])) > 0 else '_'
                                  for f in features]),
            print >>o, ""
            print >>s, str(spans[j][0]), str(spans[j][1]),
            print >>s, "\t", str(note_id)
        print >>o, ""
        print >>s, ""
    o.close()
    s.close()
