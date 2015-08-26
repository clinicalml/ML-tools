# This program loads some of the RRF files created by the Metamorphosys
# subset creator, and writes a text and/or pickle version of UMLS

import string
import pickle

f = open('MRCONSO.RRF')
mrconso = f.readlines()
f.close()
mrconso = map(lambda x: x.split('|'), mrconso)
foo = map(aux, mrconso)

concepts = {}
strtoid = {}
nametoid = {}
cuilist = []

index = 0

for (i, ls) in enumerate(mrconso):
    if i % 10000 == 0:
        print i
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
        concepts[cui]['synonyms'] = []
        concepts[cui]['types'] = []
    if ls[2] == 'P' and ls[4] == 'PF':
            concepts[cui]['name'] = st
            nametoid[st] = concepts[cui]['id']
    if st not in concepts[cui]['strings']:
        concepts[cui]['strings'] += [st]
        strtoid[st] = concepts[cui]['id']

pprint(concepts[cuilist[strtoid['fevers']]])

f = open('MRREL.SY.RRF')
syns = f.readlines()
f.close()

syns = map(lambda x: x.split('|'), syns)
syns = map(lambda x: (x[0], x[4]), syns)
syns = filter(lambda x: not (x[0] == x[1]), syns)

for (a, b) in syns:
    if a in concepts and b in concepts:
        concepts[a]['synonyms'] += [concepts[b]['id']]

f = open('MRREL.PAR.RRF')
syns = f.readlines()
f.close()

syns = map(lambda x: x.split('|'), syns)
syns = map(lambda x: (x[0], x[4]), syns)
syns = filter(lambda x: not (x[0] == x[1]), syns)
syns = list(set(syns))

for (a, b) in syns:
    if a in concepts and b in concepts:
        concepts[a]['parents'] += [concepts[b]['id']]
        concepts[b]['children'] += [concepts[a]['id']]


f = open('MRREL.AQ.RRF')
syns = f.readlines()
f.close()

syns = map(lambda x: x.split('|'), syns)
syns = map(lambda x: (x[0], x[4]), syns)
syns = filter(lambda x: not (x[0] == x[1]), syns)
syns = list(set(syns))

for (a, b) in syns:
    if a in concepts and b in concepts:
        concepts[a]['qualified'] += [concepts[b]['id']]
        concepts[b]['qualifies'] += [concepts[a]['id']]


f = open('MRREL.RB.RRF')
syns = f.readlines()
f.close()

syns = map(lambda x: x.split('|'), syns)
syns = map(lambda x: (x[0], x[4]), syns)
syns = filter(lambda x: not (x[0] == x[1]), syns)
syns = list(set(syns))

for (a, b) in syns:
    if a in concepts and b in concepts:
        concepts[a]['broader'] += [concepts[b]['id']]
        concepts[b]['narrower'] += [concepts[a]['id']]

f = open('MRSTY.RRF')
sty = f.readlines()
f.close()

for li in sty:
    ls = li.split('|')
    cui = ls[0]
    ty = ls[3]
    if cui in concepts and ty not in concepts[cui]['types']:
        concepts[cui]['types'] += [ty]

pickle.dump([concepts, cuilist, strtoid, nametoid], open('pyUMLS.k', 'w'))

f = open('UMLSlite.dat', 'w')

keyset = ['cui', 'name', 'id', 'types', 'strings', 'narrower', 'broader',
          'synonyms', 'qualifies', 'qualified', 'children', 'parents']

keyset = keyset[:5]
for k in keyset:
    print >>f, k, '||||',

print >>f, ''

ct = 0.
for cu in cuilist:
    if ct % 50000 == 0:
        print (100*ct)/len(cuilist)
    for k in keyset[:8]:
        print >>f, concepts[cu][k], '||||',
    print>>f, ''
    ct += 1


f.close()
