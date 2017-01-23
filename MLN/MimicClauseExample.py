import cPickle as pickle
import csv
import os

mimic_split_path = "/data/ml2/jernite/MIMIC3/Parsed/MIMIC3_split/"
split_dirs = sorted(os.listdir(mimic_split_path))
"""grep may_treat /data/ml2/jernite/UMLS2016/2016AA/META/MRREL.RRF
   > MRREL_may_treat.RRF"""
mrrel_treat = "/data/ml2/katrina/code_yacine/MRREL_may_treat.RRF"
"""grep contraindicated_with_disease /data/ml2/jernite/UMLS2016/
   2016AA/META/MRREL.RRF > MRREL_contraindicated.RRF"""
mrrel_contra = "/data/ml2/katrina/code_yacine/MRREL_contraindicated.RRF"
CUIlist_file = "/data/ml2/katrina/code_yacine/CUIlist.pk"

# Create dictionary of MIMIC CUIs that appear more than 10 times
CUIdict = dict([(cui, True)
               for cui, ct in pickle.load(open(CUIlist_file)) if ct >= 10])

# Function reading MRREL file and returning a dictionary


def read_mrrel(mrrel_file, CUIdict):
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
                print "Reading MRREL...", cui1, rel, rela, cui2
            if CUIdict.get(cui1, False):
                mrrel[cui1] = mrrel.get(cui1, {})
                mrrel[cui1][cui2] = mrrel[cui1].get(cui2,
                                                    {'rels': [], 'True': 0,
                                                     'False': 0})
                mrrel[cui1][cui2]['rels'] = list(set(mrrel[cui1][cui2]['rels'] +
                                                     [(rel, rela, src)]))
        csvfile.close()
    return mrrel

# Function taking a disease and returning a clause


def clause3(disease, mrrel):
    def clause_eval(adm):
        val = True
        if disease in adm['DIAGNOSES']:
            if mrrel.get(disease, False):
                appears = False
                for drug in adm['PRESCRIPTIONS'] + adm['PROCEDURES']:
                    if drug in mrrel[disease]:
                        appears = True
                        break
                if not(appears):
                    val = False
        return val
    return clause_eval

"""
Function counting number of times different DIAGNOSES,
PRESCRIPTIONS, or PROCEDURES appear in MIMIC
Arg:  DIAGNOSES, PRESCRIPTIONS, or PROCEDURES
Returns: a dictionary with counts
"""


def count_term(term):
    print "Counting number of", term, "appearing in MIMIC..."
    term_cnts = {}
    for d in split_dirs:
        # print "Reading directory", d
        admissions = None
        try:
            admissions = pickle.load(open(mimic_split_path + d +
                                          "/admission_summaries_" +
                                          d + ".pk", "rb"))
        except:
            # print "No pk file in directory", d
            continue
        for admission in admissions:
            for diag_cui in admission[term]:
                term_cnts[diag_cui] = term_cnts.get(diag_cui, 0)
                term_cnts[diag_cui] += 1
    print "Total number of", term, \
          "appearing in MIMIC admissions:", sum(term_cnts.values())
    return term_cnts

# Function counting total number of admissions


def count_adm():
    print "Counting total number of admissions in MIMIC..."
    cnt = 0
    for d in split_dirs:
        # print "Reading directory", d
        admissions = None
        try:
            admissions = pickle.load(open(mimic_split_path + "/summaries" +
                                     "/admission_summaries_" + d + ".pk", "rb"))
        except:
            # print "No pk file in directory", d
            continue
        cnt += len(admissions)
    print "Total number of MIMIC admissions:", cnt
    return cnt

# Read relations from MRREL
rel_treat = read_mrrel(mrrel_treat, CUIdict)
# rel_contra = read_mrrel(mrrel_contra, CUIdict)

# Count the total number of admissions
tot_adm = count_adm()

# Count number of times a disease appears in the dataset
dis = count_term("DIAGNOSES")
pickle.dump(dis, open("diseases.pk", "wb"))
print "Saved disease counts: /data/ml2/katrina/code_yacine/diseases.pk"
tot_dis = sum(dis.values())

# Dictionary storing truth values of disease clauses
dis_cl = dict([(cui, tot_adm) for cui in dis])

# Global count for Clause 3
global_clause3 = tot_dis

# Iterate through admissions
print "Evaluating Clause 3: All disease x, Exists Drug y, Treats(x,y)"
for d in split_dirs:
    # print "Reading directory", d
    admissions = None
    try:
        admissions = pickle.load(open(mimic_split_path + d +
                                 "/admission_summaries_" + d + ".pk", "rb"))
    except:
        # print "No pk file in directory", d
        continue
    for admission in admissions:
        for disease in admission['DIAGNOSES']:
            global_cl = True
            clause_eval = clause3(disease, rel_treat)
            if not(clause_eval(admission)):
                dis_cl[disease] -= 1
                global_cl = False
            if not(global_cl):
                global_clause3 -= 1

pickle.dump(dis_cl, open("dis_cl.pk", "wb"))

print "Global count for Clause 3:", global_clause3, \
      "True ratio:", global_clause3/float(tot_dis)
