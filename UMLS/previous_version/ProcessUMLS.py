# This program loads some of the RRF files created by the Metamorphosys
# subset creator, and writes a text and/or pickle version of UMLS

import string
import pickle
import argparse
import glob
import sys
import os
from os.path import join as pjoin

write_pickle = False
pickle_file = 'pyUMLS.pk'
write_text = False
text_file = 'UMLSlite.dat'
write_rels = False
METAdir = 'Data/UMLS2012AB/META'


def read_concepts(METAdir):
    i = 0
    index = 0
    concepts = {}
    strtoid = {}
    nametoid = {}
    cuilist = []
    f = open(pjoin(METAdir, 'MRCONSO.RRF'))
    for line in f:
        if i % 100000 == 0:
            print 'concepts:', i, 'lines read'
        i += 1
        ls = line.strip().split('|')
        if not ls[1] == 'ENG':
            continue    # only treat english language concepts
        cui = ls[0]
        st = ls[14].lower()
        if cui not in concepts:
            concepts[cui] = {}
            concepts[cui]['id'] = index
            index += 1
            cuilist += [cui]
            concepts[cui]['cui'] = cui
            concepts[cui]['strings'] = []
            concepts[cui]['parents'] = []
            concepts[cui]['children'] = []
            concepts[cui]['broader'] = []
            concepts[cui]['narrower'] = []
            concepts[cui]['qualifies'] = []
            concepts[cui]['qualified'] = []
            concepts[cui]['types'] = []
        if ls[2] == 'P' and ls[4] == 'PF':
                concepts[cui]['name'] = st
                nametoid[st] = concepts[cui]['id']
        if st not in concepts[cui]['strings']:
            concepts[cui]['strings'] += [st]
            strtoid[st] = concepts[cui]['id']
    f.close()
    return concepts, strtoid, nametoid, cuilist


def read_relations(METAdir, concepts):
    i = 0
    f = open(pjoin(METAdir, 'MRREL.RRF'))
    for line in f:
        if i % 100000 == 0:
            print 'relations:', i, 'lines read'
        i += 1
        ls = line.strip().split('|')
        (a, b) = (ls[0], ls[4])
        rel_type = ls[3]
        if rel_type == 'PAR':
            if a in concepts and b in concepts:
                concepts[a]['parents'] += [concepts[b]['id']]
                concepts[b]['children'] += [concepts[a]['id']]
        elif rel_type == 'AQ':
            if a in concepts and b in concepts:
                concepts[a]['qualified'] += [concepts[b]['id']]
                concepts[b]['qualifies'] += [concepts[a]['id']]
        elif rel_type == 'RB':
            if a in concepts and b in concepts:
                concepts[a]['broader'] += [concepts[b]['id']]
                concepts[b]['narrower'] += [concepts[a]['id']]
    f.close()


def read_sem_types(METAdir, concepts):
    i = 0
    f = open(pjoin(METAdir, 'MRSTY.RRF'))
    for line in f:
        if i % 100000 == 0:
            print 'types:', i, 'lines read'
        i += 1
        ls = line.split('|')
        (cui, ty) = (ls[0], ls[3])
        if cui in concepts and ty not in concepts[cui]['types']:
            concepts[cui]['types'] += [ty]
    f.close()


def write_text_umls(concepts, cuilist):
    global text_file
    global write_rels
    f = open(text_file, 'w')
    keyset = ['cui', 'name', 'id', 'types', 'strings', 'narrower', 'broader',
              'qualifies', 'qualified', 'children', 'parents']
    if not write_rels:
        keyset = keyset[:5]
    for k in keyset:
        print >>f, k, '||||',
    print >>f, ''
    ct = 0.
    for cui in cuilist:
        if ct % 50000 == 0:
            print (100*ct)/len(concepts), 'written'
        for k in keyset[:8]:
            print >>f, concepts[cui][k], '||||',
        print>>f, ''
        ct += 1
    f.close()


def main():
    global METAdir
    global write_pickle
    global write_text
    global pickle_file
    print 'Reading concepts'
    concepts, strtoid, nametoid, cuilist = read_concepts(METAdir)
    print 'Reading relations'
    read_relations(METAdir, concepts)
    print 'Reading types'
    read_sem_types(METAdir, concepts)
    if write_pickle:
        print 'Writing pickle'
        pickle.dump([concepts, cuilist, strtoid, nametoid],
                    open(pickle_file, 'w'))
    if write_text:
        print 'Writing text'
        write_text_umls(concepts, cuilist)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This program takes some \
     of the RRF files output by the Metamorphosys subset creator, and parses \
     them into a lighter text or pickle format')
    parser.add_argument("-data", "--umls_data",
                        help="location of the UMLS installation directory \
                              (hint: should contain a META and a NET folder)")
    parser.add_argument("-po", "--pickle_out",
                        help="pickle format output (optional)")
    parser.add_argument("-o", "--text_out",
                        help="text format output")
    parser.add_argument("-rels", "--write_rels",
                        help="writes relations (qualifies, broader than, \
                         etc...) in the text output", action="store_true")
    args = parser.parse_args()
    if args.umls_data:
        METAdir = os.path.abspath(pjoin(args.data, 'META'))
    if args.pickle_out:
        pickle_file = os.path.abspath(args.pickle_out)
        write_pickle = True
    if args.text_out:
        text_file = os.path.abspath(args.text_out)
        write_text = True
    if args.write_rels:
        write_rels = True
    assert write_pickle or write_text, 'You are not saving anything'
    print 'Starting'
    main()
