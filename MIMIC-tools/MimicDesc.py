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
                                                       'CHARTTIME'
                                                       'VALUE', 'VALUENUM', 'VALUEUOM',
                                                       'FLAG']

        self.fields['MICROBIOLOGYEVENTS_DATA_TABLE.csv'] = ['ROW_ID',
                                                            'SUBJECT_ID', 'HADM_ID',
                                                            'CHARTDATE', 'CHARTTIME',
                                                            'SPEC_ITEM_ID', 'SPEC_TYPE_CD',
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
        self.indices['NTE']     = dict([(f, i)
                                        for i, f in enumerate(self.fields['NOTEEVENTS_DATA_TABLE.csv'])])

