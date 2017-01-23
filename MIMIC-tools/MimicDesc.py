from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from os.path import join as pjoin

from Utils import *

class MimicDesc:


    # TODO: build automatically from directory
    def __init__(self):
        self.fields = {}

        self.fields['PATIENTS_DATA_TABLE.csv']  = ['ROW_ID',
                                                   'SUBJECT_ID',
                                                   'GENDER',
                                                   'DOB',
                                                   'DOD', 'DOD_HOSP', 'DOD_SSN',
                                                   'HOSPITAL_EXPIRE_FLAG']

        self.fields['ADMISSIONS_DATA_TABLE.csv'] = ['ROW_ID',
                                                    'SUBJECT_ID', 'HADM_ID',
                                                    'ADMITTIME', 'DISCHTIME', 'DEATHTIME',
                                                    'ADMISSION_TYPE', 'ADMISSION_LOCATION',
                                                    'DISCHARGE_LOCATION',
                                                    'INSURANCE',
                                                    'LANGUAGE', 'RELIGION', 'MARITAL_STATUS', 'ETHNICITY',
                                                    'DIAGNOSIS',
                                                    'HAS_IOEVENTS_DATA', 'HAS_CHARTEVENTS_DATA']   

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
                                                       'ITEMID',
                                                       'CHARTTIME',
                                                       'VALUE', 'VALUENUM', 'UOM',
                                                       'FLAG']

        self.fields['MICROBIOLOGYEVENTS_DATA_TABLE.csv'] = ['ROW_ID',
                                                            'SUBJECT_ID', 'HADM_ID',
                                                            'CHARTDATE', 'CHARTTIME',
                                                            'SPEC_ITEMID', 'SPEC_TYPE_CD',
                                                            'SPEC_TYPE_DESC',
                                                            'ORG_ITEMID', 'ORG_CD', 'ORG_NAME',
                                                            'ISOLATE_NUM',
                                                            'AB_ITEMID', 'AB_CD', 'AB_NAME',
                                                            'DILUTION_TEXT', 'DILUTION_COMPARISON', 'DILUTION_VALUE',
                                                            'INTERPRETATION']

        self.fields['DRGCODES_DATA_TABLE.csv'] = ['ROW_ID', 'SUBJECT_ID', 'HADM_ID',
                                                  'DRG_TYPE', 'DRG_CODE',
                                                  'DESCRIPTION',
                                                  'DRG_SEVERITY', 'DRG_MORTALITY']

        self.fields['PRESCRIPTIONS_DATA_TABLE.csv'] = ['ROW_ID',
                                                       'SUBJECT_ID', 'HADM_ID',
                                                       'ICUSTAY_ID',
                                                       'STARTTIME', 'ENDTIME',
                                                       'DRUG_TYPE', 'DRUG', 'DRUG_NAME_POE', 'DRUG_NAME_GENERIC',
                                                       'FORMULARY_DRUG_CD',
                                                       'GSN', 'NDC',
                                                       'PROD_STRENGTH',
                                                       'DOSE_VAL_RX', 'DOSE_UNIT_RX',
                                                       'FORM_VAL_DISP', 'FORM_UNIT_DISP',
                                                       'ROUTE']

        self.fields['PROCEDURES_ICD_DATA_TABLE.csv'] = ['ROW_ID',
                                                        'SUBJECT_ID', 'HADM_ID',
                                                        'PROC_SEQ_NUM',
                                                        'ICD9_CODE']

        self.fields['DIAGNOSES_ICD_DATA_TABLE.csv']  = ['ROW_ID',
                                                        'SUBJECT_ID', 'HADM_ID',
                                                        'SEQUENCE',
                                                        'ICD9_CODE']

        self.fields['NOTEEVENTS_DATA_TABLE.csv']     = ['ROW_ID', 'RECORD_ID',
                                                        'SUBJECT_ID', 'HADM_ID',
                                                        'CHARTDATE',
                                                        'CATEGORY', 'DESCRIPTION',
                                                        'CGID',
                                                        'ISERROR',
                                                        'TEXT']

        self.indices = {}
        self.indices['PTT']     = dict([(f, i)
                                        for i, f in enumerate(self.fields['PATIENTS_DATA_TABLE.csv'])])
        self.indices['ADM']     = dict([(f, i)
                                        for i, f in enumerate(self.fields['ADMISSIONS_DATA_TABLE.csv'])])

        self.indices['CPT']     = dict([(f, i)
                                        for i, f in enumerate(self.fields['CPTEVENTS_DATA_TABLE.csv'])])
        self.indices['ICU']     = dict([(f, i)
                                        for i, f in enumerate(self.fields['ICUSTAYEVENTS_DATA_TABLE.csv'])])
        self.indices['LAB']     = dict([(f, i)
                                        for i, f in enumerate(self.fields['LABEVENTS_DATA_TABLE.csv'])])
        self.indices['MIC']     = dict([(f, i)
                                        for i, f in enumerate(self.fields['MICROBIOLOGYEVENTS_DATA_TABLE.csv'])])
        self.indices['DRG']     = dict([(f, i)
                                        for i, f in enumerate(self.fields['DRGCODES_DATA_TABLE.csv'])]) 
        self.indices['PSC']     = dict([(f, i)
                                        for i, f in enumerate(self.fields['PRESCRIPTIONS_DATA_TABLE.csv'])]) 
        self.indices['PCD']     = dict([(f, i)
                                        for i, f in enumerate(self.fields['PROCEDURES_ICD_DATA_TABLE.csv'])])
        self.indices['DGN']     = dict([(f, i)
                                        for i, f in enumerate(self.fields['DIAGNOSES_ICD_DATA_TABLE.csv'])])
        self.indices['NTE']     = dict([(f, i)
                                        for i, f in enumerate(self.fields['NOTEEVENTS_DATA_TABLE.csv'])])


    def read_dic_files(self, dir_name):
        self.fields['D_CPT_DATA_TABLE.csv']     = ['ROW_ID',
                                                   'CATEGORY',
                                                   'SECTIONRANGE', 'SECTIONHEADER',
                                                   'SUBSECTIONRANGE', 'SUBSECTIONHEADER',
                                                   'CODESUFFIX',
                                                   'MINCODEINSUBSECTION', 'MAXCODEINSUBSECTION']

        self.fields['D_ITEMS_DATA_TABLE.csv']   = ['ROW_ID',
                                                   'ITEMID',
                                                   'LABEL', 'ABBREVIATION',
                                                   'DBSOURCE', 'LINKSTO',
                                                   'CODE', 'CATEGORY',
                                                   'UNITNAME', 'PARAM_TYPE',
                                                   'LOWNORMALVALUE', 'HIGHNORMALVALUE']

        self.fields['D_LABITEMS_DATA_TABLE.csv']        = ['ROW_ID',
                                                           'ITEMID',
                                                           'LABEL', 'FLUID', 'CATEGORY',
                                                           'LOINC_CODE']

        self.fields['D_ICD_DIAGNOSES_DATA_TABLE.csv']   = ['ROW_ID',
                                                           'ICD9_CODE',
                                                           'SHORT_TITLE', 'LONG_TITLE']

        self.fields['D_ICD_PROCEDURES_DATA_TABLE.csv']  = ['ROW_ID',
                                                           'ICD9_CODE',
                                                           'SHORT_TITLE', 'LONG_TITLE']

        self.indices['D_CPT']   = dict([(f, i)
                                        for i, f in enumerate(self.fields['D_CPT_DATA_TABLE.csv'])])
        self.indices['D_ITEMS'] = dict([(f, i)
                                        for i, f in enumerate(self.fields['D_ITEMS_DATA_TABLE.csv'])])
        self.indices['D_LABS']  = dict([(f, i)
                                        for i, f in enumerate(self.fields['D_LABITEMS_DATA_TABLE.csv'])])
        self.indices['D_DGN']   = dict([(f, i)
                                        for i, f in enumerate(self.fields['D_ICD_DIAGNOSES_DATA_TABLE.csv'])])
        self.indices['D_PCD']   = dict([(f, i)
                                        for i, f in enumerate(self.fields['D_ICD_PROCEDURES_DATA_TABLE.csv'])])

        self.dictionaries               = {}
        # D_CPT_DATA_TABLE.csv : TODO (useful?)
        # D_ITEMS_DATA_TABLE.csv: microbiology
        self.dictionaries['D_ITEMS']    = {}
        indices     = self.indices['D_ITEMS']
        file_name   = pjoin(dir_name, 'D_ITEMS_DATA_TABLE.csv')
        for split_line in read_mimic_csv(file_name):
            try:
                itemid  = split_line[indices['ITEMID']]
                label   = split_line[indices['LABEL']]
                code    = split_line[indices['CODE']]
                self.dictionaries['D_ITEMS'][itemid] = label
            except:
                print("ERROR-------- Line", split_line)
        # D_LABITEMS_DATA_TABLE.csv: labs
        self.dictionaries['D_LABS']     = {}
        indices     = self.indices['D_LABS']
        file_name   = pjoin(dir_name, 'D_LABITEMS_DATA_TABLE.csv')
        for split_line in read_mimic_csv(file_name):
            try:
                itemid  = split_line[indices['ITEMID']]
                label   = split_line[indices['LABEL']]
                code    = split_line[indices['LOINC_CODE']]
                self.dictionaries['D_LABS'][itemid] = (label, code)
            except:
                print("ERROR-------- Line", split_line)
        # D_ICD_DIAGNOSES_DATA_TABLE.csv: diagnoses
        self.dictionaries['D_DGN']      = {}
        indices     = self.indices['D_DGN']
        file_name   = pjoin(dir_name, 'D_ICD_DIAGNOSES_DATA_TABLE.csv')
        for split_line in read_mimic_csv(file_name):
            try:
                icd9    = split_line[indices['ICD9_CODE']]
                name_s  = split_line[indices['SHORT_TITLE']]
                name_l  = split_line[indices['LONG_TITLE']]
                self.dictionaries['D_DGN'][icd9] = (name_s, name_l)
            except:
                print("ERROR-------- Line", split_line)
        # D_ICD_PROCEDURES_DATA_TABLE.csv: procedures
        self.dictionaries['D_PCD']      = {}
        indices     = self.indices['D_PCD']
        file_name   = pjoin(dir_name, 'D_ICD_PROCEDURES_DATA_TABLE.csv')
        for split_line in read_mimic_csv(file_name):
            try:
                icd9    = split_line[indices['ICD9_CODE']]
                name_s  = split_line[indices['SHORT_TITLE']]
                name_l  = split_line[indices['LONG_TITLE']]
                self.dictionaries['D_PCD'][icd9] = (name_s, name_l)
            except:
                print("ERROR-------- Line", split_line)



