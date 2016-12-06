import time

import os
import argparse
import pickle
from os.path import join as pjoin


class MimicDesc:


    def __init__(self):
        self.fields = {}
        self.fields['PATIENTS_DATA_TABLE.csv']      = ['ROW_ID',
                                                       'SUBJECT_ID',
                                                       'GENDER',
                                                       'DOB',
                                                       'DOD', 'DOD_HOSP', 'DOD_SSN',
                                                       'EXPIRE_FLAG']
        self.fields['CPTEVENTS_DATA_TABLE.csv']     = ['ROW_ID',
                                                       'SUBJECT_ID', 'HADM_ID',
                                                       'COSTCENTER',
                                                       'CHARTDATE',
                                                       'CPT_CD', 'CPT_NUMBER', 'CPT_SUFFIX',
                                                       'TICKET_ID_SEQ',
                                                       'SECTIONHEADER', 'SUBSECTIONHEADER', 'DESCRIPTION']
        self.fields['ICUSTAYEVENTS_DATA_TABLE.csv'] = ['ROW_ID',
                                                       'SUBJECT_ID', 'HADM_ID',
                                                       'ICUSTAY_ID',
                                                       'DBSOURCE',
                                                       'FIRST_CAREUNIT', 'LAST_CAREUNIT',
                                                       'FIRST_WARDID', 'LAST_WARDID',
                                                       'INTIME', 'OUTTIME', 'LOS']

        self.fields['LABEVENTS_DATA_TABLE.csv']     = ['ROW_ID',
                                                       'SUBJECT_ID', 'HADM_ID',
                                                       'ITEMID', 'CHARTTIME'
                                                       'VALUE', 'VALUENUM',
                                                       'VALUEUOM',
                                                       'FLAG']

        self.fields['MICROBIOLOGYEVENTS_DATA_TABLE.csv'] = ['ROW_ID',
                                                            'SUBJECT_ID', 'HADM_ID',
                                                            'CHARTDATE', 'CHARTTIME',
                                                            'SPEC_ITEM_ID', 'SPEC_TYPE_CD',
                                                            'SPEC_TYPE_DESC', 'ORG_ITEMID',
                                                            'ORG_CD', 'ORG_NAME',
                                                            'ISOLATE_NUM', 'AB_ITEMID',
                                                            'AB_ITEMID', 'AB_CD'
                                                            'AB_NAME', 'DILUTION_TEXT'
                                                            'DILUTION_COMPARISON', 'DILUTION_VALUE',
                                                            'INTERPRETATION']

        self.fields['DRGCODES_DATA_TABLE.csv'] = ["ROW_ID", "SUBJECT_ID", "HADM_ID",
                                                  "DRG_TYPE", "DRG_CODE",
                                                  "DESCRIPTION",
                                                  "DRG_SEVERITY", "DRG_MORTALITY"]

        self.fields['PRESCRIPTIONS_DATA_TABLE.csv'] = ["ROW_ID", "SUBJECT_ID", "HADM_ID", "ICUSTAY_ID",
                                                       "STARTTIME", "ENDTIME",
                                                       "DRUG_TYPE", "DRUG", "DRUG_NAME_POE", "DRUG_NAME_GENERIC",
                                                       "FORMULARY_DRUG_CD",
                                                       "GSN", "NDC",
                                                       "PROD_STRENGTH",
                                                       "DOSE_VAL_RX", "DOSE_UNIT_RX",
                                                       "FORM_VAL_DISP", "FORM_UNIT_DISP",
                                                       "ROUTE"]
        self.fields['ADMISSIONS_DATA_TABLE.csv'] = []

        self.indices = {}
        self.indices['PATIENT'] = dict([(f, i)
                                    for i, f in enumerate(self.fields['PATIENTS_DATA_TABLE.csv'])])
        self.indices['CPT'] = dict([(f, i)
                                    for i, f in enumerate(self.fields['CPTEVENTS_DATA_TABLE.csv'])])
        self.indices['ICU'] = dict([(f, i)
                                    for i, f in enumerate(self.fields['ICUSTAYEVENTS_DATA_TABLE.csv'])])
        self.indices['LAB'] = dict([(f, i)
                                    for i, f in enumerate(self.fields['LABEVENTS_DATA_TABLE.csv'])])
        self.indices['MICROBIO'] = dict([(f, i)
                                    for i, f in enumerate(self.fields['MICROBIOLOGYEVENTS_DATA_TABLE.csv'])])
        self.indices['DRG'] = dict([(f, i)
                                    for i, f in enumerate(self.fields['DRGCODES_DATA_TABLE.csv'])])
        self.indices['PSC'] = dict([(f, i)
                                    for i, f in enumerate(self.fields['PRESCRIPTIONS_DATA_TABLE.csv'])])


class MimicPatient:

    def __init__(self, line, mimic_desc):
        self.mimic_desc    = mimic_desc

        tab                = line.strip().split(',')
        #print tab
        indices            = mimic_desc.indices['PATIENT']
        #print indices
        self.patient_id    = tab[indices['SUBJECT_ID']]
        self.gender        = tab[indices['GENDER']]
        self.dob           = tab[indices['DOB']]
        self.dod           = ''
        if len(tab[indices['DOD']]) > 0:
            self.dod       = tab[indices['DOD']]
        elif len(tab[indices['DOD_HOSP']]) > 0:
            self.dod       = tab[indices['DOD_HOSP']]
        else:
            self.dod       = tab[indices['DOD_SSN']]
        self.expire_flag   = tab[indices['EXPIRE_FLAG']]
        # Maps admission_ids to admission class object
        self.admissions    = {}


"""
Funciton reading a file and creating a dictionary
mapping patient ids to MIMIC patient objects

Args:
- file_loc: location of patient file

Outputs: a dictionary with patient ids and
         corresponding MimicPatient objects
"""

def read_patient(file_loc):
    # Dictionary to store patient info
    patients = {}
    # Patient data attributes
    mimic_desc = MimicDesc()
    # Read file
    f = None
    try:
        file_name = pjoin(file_loc, 'PATIENTS_DATA_TABLE.csv')
        f = open(file_name, 'rb')
    except:
        print "File", file_name, "not found."
        # Return empty dictionary
        return patients
    for i, line in enumerate(f):
        try:
            obs = MimicPatient(line, mimic_desc)
            #print obs.patient_id
            if obs.patient_id in patients:
                print "DUPLICATE OBSERVATIONS FOR PATIENT_ID:", obs.patient_id
            else:
                patients[obs.patient_id] = obs
        except:
            print "Line", i, "in file", file_name, "not read."
    f.close()
    # Return patients dictionary
    return patients

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This program reads the \
                 MIMIC Patient files, and converts them to pickle format.')
    parser.add_argument("-loc", "--MIMIC3_folder", \
                        default='/data/ml2/MIMIC3/',
                        help="Location of the MIMIC3 Patient files.")
    args = parser.parse_args()
    #print args.MIMIC3_folder
    #for d in os.listdir(args[0]):
    for d in ['00']:
        print "directory", d
        file_loc = pjoin(args.MIMIC3_folder, d)
        patients = read_patient(file_loc)
        print patients.items()[0]
        pickle.dump(patients, open(pjoin(file_loc, "patients.pk"), "wb"))
                                                                                                                                                       165,1         Bot