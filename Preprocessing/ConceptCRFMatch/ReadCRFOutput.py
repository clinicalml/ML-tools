import argparse
import os
import numpy as np
from pprint import pprint
import cPickle as pickle

# results_file = 'crfpp_output/dev_res_c1_l2_v2.dat'
# spans_file = 'crfpp_input_dev/crfpp_spans_batch_1.txt'
results_file = 'MIMICcrf/00/mimic_00_res_c1_l2_v2.dat'
spans_file = 'MIMICcrf/00/crfpp_spans_batch_1.txt'
verbose = False
overlaps = False

thres = 0.25


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


def read_sentence(y, overlaps):
    sentence = y.splitlines()[1:]
    if overlaps:
        tags = [(token.split()[-10], token.split()[-9].split('/')[0], token.split()[-8:])
        # tags = [(token.split()[-10], token.split()[-10], token.split()[-8:])
           for token in sentence if len(token) > 0]
    else:
        tags = [(token.split()[-7], token.split()[-6].split('/')[0], token.split()[-5:])
               for token in sentence if len(token) > 0]
    text = [token.split()[0] for token in sentence if len(token) > 0]
    gold = tags_to_mentions([tag[0] for tag in tags])
    pre_found = tags_to_mentions([tag[1] for tag in tags])
    found = [(x, 1) for x in pre_found]
    return [' '.join(text), gold, found]


def treat_sentences(results_file, overlaps):
    sentences = []
    ct = 0
    f = open(results_file)
    y = []
    for line in f:
        if line.startswith('# '):
            if len(y) > 0:
                ct += 1
                sentences += [read_sentence(''.join(y), overlaps)]
            y = [line]
        else:
            y = y + [line]
    sentences += [read_sentence(''.join(y), overlaps)]
    f.close()
    return sentences


def explore(sentences, idx, thres):
    split = False
    sentence = sentences[idx]
    print sentence[0]
    words = sentence[0].split()
    gold = sentence[1]
    seen = dict([(men, False) for men in gold])
    for mention in sentence[2]:
        if(mention[1]) < thres and not split:
            split = True
            print thres, '.....................'
        if mention[0] in gold:
            seen[mention[0]] = True
            print '++++++', '\t', mention[0], '\t',
        else:
            print '------', '\t', mention[0], '\t',
        for wn in mention[0]:
            print words[wn],
        print '\t', mention[1]
    if not split:
        print thres, '.....................'
    for men, done in seen.items():
        if not done:
            print 'missed', '\t', men,
            for wn in men:
                print words[wn],
            print ''


def main():
    sentences = treat_sentences(results_file, overlaps)
    for i in range(len(sentences)):
        if len(sentences[i][1]) > 3:
            explore(sentences, i, 0.2)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This program takes the \
        output of crf++ predict and computes accuracy')
    parser.add_argument("-pr", "--predictions",
                        help="output of crf++")
    parser.add_argument("-v", "--verbose",
                        help="increase output verbosity", action="store_true")
    parser.add_argument("-ov", "--overlaps",
                        help="when using overlap tags", action="store_true")
    args = parser.parse_args()
    if args.predictions:
        results_file = os.path.abspath(args.predictions)
    if args.verbose:
        verbose = True
    if args.overlaps:
        overlaps = True
    main()
