from MimicDesc import *

class MimicEvent:


    def __init__(self, patients, indices, split_line):
        patient_id      = split_line[indices['SUBJECT_ID']]
        admission_id    = split_line[indices['HADM_ID']]

        try:
            self.patient    = patients[patient_id]
        except:
            print 'ERROR--------', '\t', 'PATIENT NOT FOUND', patient_id

        try:
            self.admission  = self.patient.admissions[admission_id]
        except:
            print 'ERROR--------', '\t', 'ADMISSION NOT FOUND', patient_id, admission_id

        self.date       = None
        self.start_time = None
        self.end_time   = None

# CPTEVENTS_DATA_TABLE.csv
class CptEvent(MimicEvent):


    def __init__(self, patients, mimic_desc, split_line):
        indices         = mimic_desc.indices['CPT']
        super(MimicEvent, self).__init__(patients, indices, split_line)

        self.date       = split_line[indices['CHARTDATE']]

        self.cpt_info   = (split_line[indices['SECTIONHEADER']],
                           split_line[indices['SUBSECTIONHEADER']],
                           split_line[indices['DESCRIPTION']])

        self.codes      = (split_line[indices['CPT_CD']],
                           split_line[indices['CPT_NUMBER']],
                           split_line[indices['CPT_SUFFIX']])

        self.admission.cpt_events += [self]

# ICUSTAYEVENTS_DATA_TABLE.csv
class IcuEvent(MimicEvent):


    def __init__(self, patients, mimic_Desc, split_line):
        indices         = mimic_desc.indices['ICU']
        super(MimicEvent, self).__init__(patients, indices, split_line)

        self.start_time = split_line[indices['INTIME']]
        self.end_time   = split_line[indices['OUTIME']]

        self.icu_length = split_line[indices['LOS']]
        self.icu_id     = split_line[indices['ICUSTAY_ID']]
        self.icu_info   = (split_line[indices['FIRST_CAREUNIT']],
                           split_line[indices['LAST_CAREUNIT']])

        self.admission.icu_events += [self]

# LABEVENTS_DATA_TABLE.csv
class LabEvent(MimicEvent):


    def __init__(self, patients, mimic_Desc, split_line):
        indices         = mimic_desc.indices['LAB']
        super(MimicEvent, self).__init__(patients, indices, split_line)

        self.start_time = split_line[indices['CHARTTIME']]
        self.end_time   = split_line[indices['CHARTTIME']]

        self.lab_id     = split_line[indices['ITEMID']]
        self.lab_value  = (split_line[indices['VALUE']],
                           split_line[indices['VALUENUM']],
                           split_line[indices['VALUEOM']])
        # normal or abnormal
        self.lab_flag   = split_line[indices['FLAG']]

        self.admission.lab_events += [self]

# MICROBIOLOGYEVENTS_DATA_TABLE.csv
class MicroEvent(MimicEvent):


    def __init__(self, patients, mimic_Desc, split_line):
        indices         = mimic_desc.indices['MIC']
        super(MimicEvent, self).__init__(patients, indices, split_line)

        self.start_time      = split_line[indices['CHARTTIME']]
        self.end_time        = split_line[indices['CHARTTIME']]

        self.date            = split_line[indices['CHARTDATE']]

        self.code            = split_line[indices['SPEC_TYPE_CD']]
        self.item_id         = split_line[indices['SPEC_ITEMID']]

        self.description     = split_line[indices['SPEC_TYPE_DESC']]
        self.dilution        = (split_line[indices['DILUTION_TEXT']], 
                                split_line[indices['DILUTION_COMPARISON']],
                                split_line[indices['DILUTION_VALUE']])

        self.interpretation   = split_line[indices['INTERPRETATION']]

        self.admission.mic_events += [self]

# DRGCODES_DATA_TABLE.csv
class DrugEvent(MimicEvent):


    def __init__(self, patients, mimic_Desc, split_line):
        indices         = mimic_desc.indices['DRG']
        super(MimicEvent, self).__init__(patients, indices, split_line)

        self.drg_codes   = (split_line[indices['DRG_TYPE']],
                            split_line[indices['DRG_CODE']])

        self.description = split_line[indices['DESCRIPTION']]

        self.severity    = (split_line[indices['DRG_SEVERITY']],
                            split_line[indices['DRG_MORTALITY']])

        self.admission.drg_events += [self]

# PRESCRIPTIONS_DATA_TABLE.csv
class PrescriptionEvent(MimicEvent):


    def __init__(self, patients, mimic_Desc, split_line):
        indices         = mimic_desc.indices['PSC']
        super(MimicEvent, self).__init__(patients, indices, split_line)

        self.start_time    = split_line[indices['STARTTIME']]
        self.end_time      = split_line[indices['ENDTIME']]

        self.icu_id        = split_line[indices['ICUSTAY_ID']]

        self.drug_type     = split_line[indices['DRUG_TYPE']]
        self.drug_names    = (split_line[indices['DRUG']],
                              split_line[indices['DRUG_NAME_POE']],
                              split_line[indices['DRUG_NAME_GENERIC']])
        self.drug_codes    = (split_line[indices['FORMULARY_DRUG_CD']],
                              split_line[indices['GSN']],
                              split_line[indices['NDC']])
        self.drug_info     = (split_line[indices['PROD_STRENGTH']],
                              split_line[indices['DOSE_VAL_RX']],
                              split_line[indices['DOSE_UNIT_RX']],
                              split_line[indices['FORM_VAL_DISP']],
                              split_line[indices['FORM_UNIT_DISP']],
                              split_line[indices['ROUTE']])

        self.admission.psc_events += [self]

# PROCEDURES_ICD_DATA_TABLE.csv 
class ProcedureEvent(MimicEvent):


    def __init__(self, patients, mimic_Desc, split_line):
        indices         = mimic_desc.indices['PCD']
        super(MimicEvent, self).__init__(patients, indices, split_line)

        self.seq_no     = split_line[indices['PROC_SEQ_NUM']]
        self.code       = split_line[indices['ICD9_CODE']]
        
        self.admission.pcd_events += [self]

# NOTEEVENTS_DATA_TABLE.csv 
class NoteEvent(MimicEvent):


    def __init__(self, patients, mimic_Desc, split_line):
        indices         = mimic_desc.indices['NTE']
        super(MimicEvent, self).__init__(patients, indices, split_line)

        self.date       = split_line[indices['CHARTDATE']]
        self.note_cat   = split_line[indices['CATEGORY']]
        self.note_desc  = split_line[indices['DESCRIPTION']]

        self.care_giver = split_line[indices['CGID']]
        self.erroneous  = split_line[indices['ISERROR']]

        self.note_text  = split_line[indices['TEXT']]
        
        self.admission.nte_events += [self]
