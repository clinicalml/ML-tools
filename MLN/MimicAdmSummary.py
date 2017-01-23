import cPickle as pickle
import csv
import os

from pprint import pprint

from make_dictionaries import *

mimic_split_path = "/data/ml2/jernite/MIMIC3/Parsed/MIMIC3_split/"
split_dirs = sorted(os.listdir(mimic_split_path))

# Make dictionaries
ndc_to_cui, icd9_to_cui = make_dics(ndc_file, rxcui_file, icd9_file)

# Get relevant CUIs for all admissions
cui_counts = {}
for d in split_dirs:
    print "Reading directory", d
    # Read admissions pickle file
    try:
        admissions = pickle.load(open(mimic_split_path + d +
                                      "/admissions_" + d + ".pk", "rb"))
    except:
        admissions = []
        print "no pk file in directory", d
    if len(admissions) > 0:
        admission_summaries = [admission_summary(admission, ndc_to_cui,
                                                 icd9_to_cui)
                               for admission in admissions]
        for summary in admission_summaries:
            for val in summary.values():
                for cui in val:
                    cui_counts[cui] = cui_counts.get(cui, 0) + 1
        pickle.dump(admission_summaries,
                    open(mimic_split_path + d +
                         "/admission_summaries_" + d + ".pk", "wb"))

pickle.dump(sorted(cui_counts.items(), key=lambda x: x[1], reverse=True),
            open("CUIlist.pk", "wb"))
