import cPickle as pickle
import csv
import os

from pprint import pprint

from make_dictionaries import *

mimic_split_path = '/data/ml2/jernite/MIMIC3/Parsed/MIMIC3_split/'
mrrel_file = '/data/ml2/jernite/UMLS2016/2016AA/META/MRREL.RRF'
CUIlist_file = '/data/ml2/katrina/code_yacine/CUIlist.pk'

split_dirs = sorted(os.listdir(mimic_split_path))
CUIdict = dict([(cui, True)
               for cui, ct in pickle.load(open(CUIlist_file)) if ct >= 10])

# Read relations from MRREL
print 'Loading MRREL.RRF'
mrrel = {}
lines_read = 0
with open(mrrel_file, "rb") as csvfile:
    reader = csv.reader(csvfile, delimiter="|")
    for row in reader:
        lines_read += 1
        cui1 = row[0]
        cui2 = row[4]
        rel = row[3]
        rela = row[7]
        src = row[10]
        if lines_read % 4e5 == 0:
            print "Reading MRREL...", cui1, rel, rela, cui2, src
        if CUIdict.get(cui1, False):
            mrrel[cui1] = mrrel.get(cui1, {})
            mrrel[cui1][cui2] = mrrel[cui1].get(cui2, [])
            mrrel[cui1][cui2] += [(rel, rela, src)]
    csvfile.close()


# Function returning all possible pairs among elements in a list
def all_pairs(vals):
    return [(val_a, val_b)
            for i, val_a in enumerate(vals)
            for j, val_b in enumerate(vals) if val_a != val_b]

# Dictionary saving CUI combinations from MIMIC and their appearances in MRREL
mimic_rels = {}

# For each admission get all CUI combinations
for d in split_dirs:
    print "Reading directory", d
    # Read admissions pickle file
    try:
        admissions = pickle.load(open(mimic_split_path + d +
                                      "/admission_summaries_" +
                                      d + ".pk", "rb"))
    except:
        admissions = []
        print "no pk file in directory", d
    for admission in admissions:
        cui_list = [cui for cuis in admission.values() for cui in cuis]
        # All possible pairs among admission CUIs
        for cui1, cui2 in all_pairs(cui_list):
            # Check whether pair appears in MRREL
            if mrrel.get(cui1, {}).get(cui2, False):
                # print cui1, cui2, mrrel[cui1][cui2][0]
                mimic_rels[cui1] = mimic_rels.get(cui1, {})
                mimic_rels[cui1][cui2] = mimic_rels[cui1].get(cui2, {'rels': mrrel[cui1][cui2], 'in_MIMIC': 0})
                mimic_rels[cui1][cui2]['in_MIMIC'] += 1
    print(sum([len(m_rel) for m_rel in mimic_rels.values()]))

# Save number of co-occurances of MIMIC CUIs in UMLS MRREL}
pickle.dump(mimic_rels, open("mimic_evidence_yacine.pk", "wb"))
