# Deal with overlapping mentions better

import os
import re
import argparse
import glob
import sys
import numpy as np
import cPickle as pickle
import xml.etree.ElementTree as et
from string import punctuation as punct
from os.path import join as pjoin
from pprint import pprint
from multiprocessing import Pool
import marisa_trie

from ReadUMLS import *
from StanNLPInterface import *

datadir = '../data/train'
UMLSfile = '../data/UMLStok.dat'
concepts_file = 'mentions'
# suff = '.text'		# --TODO: fix
suff = ''

remove_r = False		# TODO: fix

outputdir = 'crfpp_input'
batch_size = 0
num_threads = 1
verbose = True
max_rep = 10
has_tags = False
window = 2

tag_type = 'basic'

use_umls = True
extract_concepts = False
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


#~ # rest
#~ features = ['word', 'lemma', 'pos',
            #~ 'prefix', 'suffix',
            #~ 'umls_match_tag_full']

#~ # wpsu
#~ features = ['word', 'prefix', 'suffix',
            #~ 'umls_match_tag_full']

#~ # wpu
#~ features = ['word', 'pos', 'umls_match_tag_full']

#~ # wu
#~ features = ['word', 'umls_match_tag_full']

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
        if use_umls:
            med_prefix = find_word_prefixes(words, spelling_trie)
            full_matches, prefix_matches, acro_matches = \
                find_concepts(words, trie, prefix_trie, acro_trie)
        features = [token_features(token) for token in sent]
        for j in range(len(features)):
            features[j]['word_pos'] = min(j / 3, 10)
            features[j]['sentence_pos'] = min(i / 10, 5)
            features[j]['sentence_length'] = min(len(features) / 4, 5)
            if use_umls:
                features[j]['med_prefix'] = med_prefix[j]
                features[j]['umls_match_tag_full'] = full_matches[j]
                features[j]['umls_match_tag_prefix'] = prefix_matches[j]
                features[j]['umls_match_tag_acro'] = acro_matches[j]
        sentence = (words, spans, features)
        sentences += [sentence]
    return (note_id, sentences)


"""
# Checks whether the intervals defined by tuple1 and tuple2 intersect
def interf(tuple1, tuple2):
    if tuple1 == tuple2:
        return False
    elif tuple1[-1][1] < tuple2[0][0] or tuple1[0][0] > tuple2[-1][1]:
        return False
    return True


# This function greedily looks for a minimum covering set
# of disjoint mentions
def cover(sent):
    res = []
    missing = sent[:]
    if len(sent) == 0:
        return [[]]
    while len(missing) > 0:
        cup, priority = missing[0]
        suite = []
        for cut, tup in sent:
            if len(suite) > 0 and interf(tup, suite[-1]) or \
              interf(tup, priority):
                continue
            else:
                suite += [(cut, tup)]
                if (cut, tup) in missing:
                    missing.remove((cut, tup))
                if tup == priority:
                    i = 0
                    while i < len(missing) and interf(tup, missing[i][1]):
                        i += 1
                    if i < len(missing):
                        cup, priority = missing[i]
        res += [suite[:]]
    return sorted(res, key=len, reverse=True)
"""

# This functions takes a list of mention tags in the format provided by
# the .pip files (list of lists of character spans) and returns a list
# of lists of word indices for a sentence.
# Also returns a list of the mentions that were missed due to mistakes of
# the word and sentence tokenizer, and information about overlapping mentions
def char_spans_to_indices(sentence_spans, mentions_char_spans):
    res = []
    missed = []
    overlaps = {}
    belongs_to = [[] for w in sentence_spans]
    # char spans to word spans
    for i, (cui, m_spans) in enumerate(mentions_char_spans):
        indices = []
        t_spans = m_spans[:]
        overlaps[i] = []
        while len(t_spans) > 0:
            c_sp = t_spans[0]
            t_spans = t_spans[1:]
            for j, sp in enumerate(sentence_spans):
                if sp[1] > c_sp[0] and sp[0] < c_sp[1]:
                    indices += [j]
                    for idx in belongs_to[j]:
                        if idx not in overlaps[i]:
                            overlaps[i] += [idx]
                        if i not in overlaps[idx]:
                            overlaps[idx] += [i]
                    belongs_to[j] += [i]
        if len(indices) == 0 or m_spans[-1][1] > sentence_spans[-1][1]:
            missed += [(cui, m_spans)]
        else:
            res += [(cui, tuple(indices[:]))]
    res = tuple(sorted(res, key=lambda x: x[1]))
    return (res, missed, overlaps, belongs_to)


# This functions takes a list of mention tags output by char_spans_to_indices
# (list of lists of  word indices) and returns the sequence of tags using
# a ['B', 'I', 'ID', 'O', 'OD'] scheme. This scheme fails on about 5% of
# the sentences with at least one mention, whenever two mentions overlap
def tag_disjoint(sentence_spans, mentions_word_spans):
    tagging = ['O' for sp in sentence_spans]
    for cui, men in mentions_word_spans:
        disjoint = False
        for i in range(men[0], men[-1] + 1):
            tagging[i] = 'OD'
            if i not in men:
                disjoint = True
        for i, idx in enumerate(men):
            if i == 0:
                tagging[idx] = 'B'
            else:
                tagging[idx] = 'ID' if disjoint else 'I'
    return tagging


# This functions takes a list of mention tags output by char_spans_to_indices
# (list of lists of  word indices) and returns the sequence of tags using
# a ['B', 'Bp', 'I', 'Ip', 'In', 'ID', 'O', 'OD'] scheme. This scheme 
# accounts for most overlap, but still fails in the case of nested mentions
# which appear in 0.5% of the sentences with at least one mention
def tag_disjoint_overlap(sentence_spans, mentions_word_spans, overlaps, belongs_to):
    tagging = ['O' for sp in sentence_spans]
    for m_i, (cui, men) in enumerate(mentions_word_spans):
        disjoint = False
        new = True
        for i in range(men[0], men[-1] + 1):
            if tagging[i] == 'O':
                tagging[i] = 'OD'
            if i not in men:
                disjoint = True
        for i, idx in enumerate(men):
            if i == 0:
                if len(overlaps[m_i]) >= len(belongs_to[idx]):
                    tagging[idx] = 'Bp'
                    new = False
                else:
                    tagging[idx] = 'B'
            else:
                if len(overlaps[m_i]) >= len(belongs_to[idx]):
                    if new:
                        tagging[idx] = 'In'
                        new = False
                    else:
                        tagging[idx] = 'Ip'
                else:
                    tagging[idx] = 'ID' if disjoint else 'I'
    return tagging


# This function reads the label file for note_id (note_id + '.pipe')
# and returns a list of BIO tags
def tag_note(note_id, spans_list):
    global tag_type
    all_taggings = []
    all_mentions = []
    missed = []
    # step 1: read the labels file to extract mentions
    f = open(pjoin(datadir, note_id + '.pipe'), "r")
    mentions = [(line.split("|")[2], line.split("|")[1].split(","))
                for line in f.readlines()]
    f.close()
    mentions = [(cui, tuple([tuple(map(int, disorder_span.split("-")))
                 for disorder_span in disorder_spans]))
                for cui, disorder_spans in mentions]
    # step 2: assign those mentions to sentences
    men_per_sent = [[] for sen in spans_list]
    sent_starts = [spans[0][0] for spans in spans_list]
    cur_sent = 0
    for cui, mention in mentions:
        while cur_sent + 1 < len(spans_list) and mention[0][0] >= \
                                              sent_starts[cur_sent + 1]:
            cur_sent += 1
        men_per_sent[cur_sent] += [(cui, mention)]
    # step 3: transform numeric mention tags into BIO sequences
    sentences = []
    current_mention = []
    for i, spans in enumerate(spans_list):
        (mentions_word_spans, missed,
         overlaps, belongs_to) = char_spans_to_indices(spans,
                                                       men_per_sent[i])
        if tag_type == 'basic':
            sentence_tags = tag_disjoint(spans, mentions_word_spans)
        else:
            sentence_tags = tag_disjoint_overlap(spans,
                                                 mentions_word_spans,
                                                 overlaps, belongs_to)
        all_mentions += [(cui, tuple([(i, j) for j in men]))
                         for cui, men in mentions_word_spans]
        all_taggings += [sentence_tags]
    return (all_taggings, all_mentions)


# write template
# TODO: bigram features. Example: "B14:%x[-1,27]/%x[0,27]/%x[1,27]"
def generate_crfpp_template(window):
    temp = []
    temp.append("U00")
    c = 0
    for f in features:
        for r in xrange(-window, window+1):
            c += 1
            temp.append("U" + str(c) + ":%x[" + str(int(r)) +
                        "," + str(int(features.index(f))) + "]")
    temp.append("B00")
    return "\n".join(temp)


# writes crfpp formatted data and spans file
def write_crfpp_data(note_id, sentences, all_taggings, text_file, spans_file):
    o = open(text_file, "a")
    s = open(spans_file, "a")
    for sentence, tagging in zip(sentences, all_taggings):
        words = sentence[0]
        spans = sentence[1]
        tokens = sentence[2]
        for j, token in enumerate(tokens):
            print >>o, "\t".join([str(token[f]).encode('utf-8')
                                  if len(str(token[f])) > 0 else '_'
                                  for f in features]),
            if has_tags:
                print >>o, "\t", tagging[j]
            else:
                print >>o, "\t", 'O'
            print >>s, str(spans[j][0]), str(spans[j][1]),
            print >>s, "\t", str(note_id)
        print >>o, ""
        print >>s, ""
    o.close()
    s.close()


# process function for multiprocessing
def process_batch(x):
    batch, nb = x
    print "processing batch", len(batch)
    sents = stanford_parse(batch, nb, tmpdir)
    for note in sents:
        (note_id, sentences) = extract_features(note, trie, prefix_trie,
                                                acro_trie, spelling_trie)
        spans_list = [sentence[1] for sentence in sentences]
        words_list = [sentence[0] for sentence in sentences]
        #~ pickle.dump((note_id, sentences), open(str(note_id) + '_inter.pk', 'wb'))
        if has_tags:
            (all_taggings, all_mentions) = tag_note(note_id, spans_list)
        else:
            all_taggings = [[(['O' for span in spans],
                              ['None' for span in spans])]
                            for spans in spans_list]
            all_mentions = []
        # if we are writing the mentions from the gold labels
        if extract_concepts:
            o = open(concepts_file + str(nb) + '.dat', 'a')
            for cui, words in all_mentions:
                print >>o, note_id, '\t',
                for word in words:
                    print >>o, word,
                print >>o, '\t',
                for word in words:
                    print >>o, words_list[word[0]][word[1]],
                print >>o, '\t', cui
            print >>o, '' 
            o.close()
        # if we are writing the CRF data
        else:
            write_crfpp_data(
                note_id, sentences, all_taggings,
                pjoin(outputdir, 'crfpp_text_batch_' + str(nb) + '.txt'),
                pjoin(outputdir, 'crfpp_spans_batch_' + str(nb) + '.txt')
                )
    if nb == 1 and not extract_concepts:
        template = generate_crfpp_template(window)
        with open(pjoin(outputdir, 'crfpp_template.txt'), 'w') as f:
            f.write(template)


def main():
    global UMLS, lookup, trie, prefix_trie, suffix_trie, spelling_trie, acro_trie
    # We first load UMLS
    if use_umls:
        print "reading", UMLSfile
        UMLS, lookup, trie, prefix_trie, suffix_trie, \
            spelling_trie, acro_trie = read_umls(UMLSfile)
        print prefix_trie
    file_list = glob.glob(pjoin(datadir, '*' + suff))
    os.system('mkdir ' + outputdir)
    # Then process files in the data directory in parallel
    if batch_size == 0:
        batches = [file_list]
        process_batch((file_list, 1))
    else:
        n_batches = len(file_list) / batch_size
        batches = [file_list[i * batch_size: (i+1) * batch_size]
                   for i in range(n_batches)]
        batches += [file_list[n_batches * batch_size:]]
        p = Pool(num_threads)
        print p.map(process_batch,
                    [(batches[i], i+1) for i in range(len(batches))])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This program takes all the \
     .text files in a DATA folder, does some some standard NLP and feature \
     extraction, and writes the output in a format which can be used by crf++ \
     for learning or prediction.')
    parser.add_argument("-nlp", "--corenlp",
                        help="location of the Stanford CoreNLP installation")
    parser.add_argument("-data", "--data",
                        help="location of folder containing the .txt files")
    parser.add_argument("-umls", "--umls",
                        help="UMLS text file (UMLSlite.dat)")
    parser.add_argument("-o", "--output",
                        help="output directory for the crfpp formatted files")
    parser.add_argument("-b", "--batch",
                        help="how many files to process at a time")
    parser.add_argument("-th", "--threads",
                        help="number of threads")
    parser.add_argument("-mr", "--max_rep",
                        help="maximum number of replications for a sentence")
    parser.add_argument("-t", "--tagging",
                        help="read tags from .pipe files", action="store_true")
    parser.add_argument("-tt", "--tag_type",
                        help="tagging scheme. basic or overlaps")
    parser.add_argument("-nu", "--no_umls",
                        help="does not use UMLS", action="store_true")
    parser.add_argument("-ec", "--extract_concepts",
                        help="does not use UMLS")
    parser.add_argument("-tmp", "--temp_dir",
                        help="specifies a temporary directory for StanCoreNLP")
    parser.add_argument("-r", "--return_carriage",
                        help="disables the return carriga filtering (for files \
     created in Linux or MacOS)", action="store_true")
    parser.add_argument("-v", "--verbose",
                        help="increase output verbosity", action="store_true")
    args = parser.parse_args()
    if args.corenlp:
        StanNLPdir = os.path.abspath(args.corenlp)
    if args.data:
        datadir = os.path.abspath(args.data)
    if args.umls:
        UMLSfile = os.path.abspath(args.umls)
        use_umls = True
    if args.output:
        outputdir = os.path.abspath(args.output)
    if args.batch:
        batch_size = int(args.batch)
    if args.threads:
        num_threads = int(args.threads)
    if args.max_rep:
        max_rep = args.max_rep
    if args.tagging:
        has_tags = True
    if args.tag_type:
        tag_type = args.tag_type
    if args.no_umls:
        use_umls = False
    if args.extract_concepts:
        concepts_file = os.path.abspath(args.extract_concepts)
        use_umls = False
        extract_concepts = True
        has_tags = True
    if args.temp_dir:
        tmpdir = os.path.abspath(args.temp_dir)
    if args.return_carriage:
        remove_r = False
    if args.verbose:
        verbose = True
    print 'Starting'
    main()
