from MimicDesc import *
from MimicPatient import *

class MimicEvent(object):


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
            self.patient.admissions[admission_id] = MimicAdmission(patients,
                                                                   patient_id=patient_id,
                                                                   admission_id=admission_id)
            self.admission  = self.patient.admissions[admission_id]
            print 'ERROR--------', '\t', 'ADMISSION NOT FOUND PTT', patient_id, 'ADM', admission_id, '\r',

        self.time           = self.admission.out_time

# CPTEVENTS_DATA_TABLE.csv
class CptEvent(MimicEvent):


    def __init__(self, patients, mimic_desc, split_line):
        indices         = mimic_desc.indices['CPT']
        super(CptEvent, self).__init__(patients, indices, split_line)

        self.date       = split_line[indices['CHARTDATE']]
        if self.date != '':
            self.time = self.date

        self.cpt_info   = (split_line[indices['SECTIONHEADER']],
                           split_line[indices['SUBSECTIONHEADER']],
                           split_line[indices['DESCRIPTION']])

        self.codes      = (split_line[indices['CPT_CD']],
                           split_line[indices['CPT_NUMBER']],
                           split_line[indices['CPT_SUFFIX']])

        self.admission.cpt_events += [self]


    def __str__(self):
        res = self.time + '\t' + 'CPT Event ' + '\t'
        res += str(self.cpt_info)
        return res

# ICUSTAYEVENTS_DATA_TABLE.csv
class IcuEvent(MimicEvent):


    def __init__(self, patients, mimic_desc, split_line):
        indices         = mimic_desc.indices['ICU']
        super(IcuEvent, self).__init__(patients, indices, split_line)

        self.start_time = split_line[indices['INTIME']]
        self.end_time   = split_line[indices['OUTTIME']]
        if self.start_time != '':
            self.time = self.start_time

        self.icu_length = split_line[indices['LOS']]
        self.icu_id     = split_line[indices['ICUSTAY_ID']]
        self.icu_info   = (split_line[indices['FIRST_CAREUNIT']],
                           split_line[indices['LAST_CAREUNIT']])

        self.admission.icu_events += [self]


    def __str__(self):
        res = self.time + '\t' + 'ICU Event ' + '\t'
        res += self.start_time + '\t' + self.icu_info[0] + '\t to \t'
        res += self.end_time + '\t' + self.icu_info[1]
        return res

# LABEVENTS_DATA_TABLE.csv
class LabEvent(MimicEvent):


    # TODO: map ITEMID to dictionary file D_LABITEMS  -> label and LOINC
    def __init__(self, patients, mimic_desc, split_line):
        indices         = mimic_desc.indices['LAB']
        super(LabEvent, self).__init__(patients, indices, split_line)

        self.start_time = split_line[indices['CHARTTIME']]
        self.end_time   = split_line[indices['CHARTTIME']]
        if self.start_time != '':
            self.time = self.start_time

        self.lab_id     = split_line[indices['ITEMID']]
        self.lab_value  = (split_line[indices['VALUE']],
                           split_line[indices['VALUENUM']],
                           split_line[indices['UOM']])
        # normal or abnormal
        self.lab_flag   = split_line[indices['FLAG']]

        self.admission.lab_events += [self]


    def __str__(self):
        # TODO: map ITEMID to dictionary file -> name
        res = self.time + '\t' + 'LAB Event ' + '\t'
        res += 'status' + self.lab_flag
        return res

# MICROBIOLOGYEVENTS_DATA_TABLE.csv
class MicroEvent(MimicEvent):


    # TODO: map SPEC_ITEMID to dictionary file D_ITEMS -> name
    def __init__(self, patients, mimic_desc, split_line):
        indices         = mimic_desc.indices['MIC']
        super(MicroEvent, self).__init__(patients, indices, split_line)

        self.start_time      = split_line[indices['CHARTTIME']]
        self.end_time        = split_line[indices['CHARTTIME']]
        if self.start_time != '':
            self.time = self.start_time

        self.date            = split_line[indices['CHARTDATE']]

        self.code            = split_line[indices['SPEC_TYPE_CD']]
        self.item_id         = split_line[indices['SPEC_ITEMID']]

        self.description     = split_line[indices['SPEC_TYPE_DESC']]
        self.dilution        = (split_line[indices['DILUTION_TEXT']], 
                                split_line[indices['DILUTION_COMPARISON']],
                                split_line[indices['DILUTION_VALUE']])

        self.interpretation   = split_line[indices['INTERPRETATION']]

        self.admission.mic_events += [self]


    def __str__(self):
        # TODO: map SPEC_ITEMID to dictionary file -> name
        res = self.time + '\t' + 'MICRO Event ' + '\t'
        res += self.description + '\t interpretation \t' + self.interpretation
        return res

# DRGCODES_DATA_TABLE.csv
class DrugEvent(MimicEvent):


    def __init__(self, patients, mimic_desc, split_line):
        indices         = mimic_desc.indices['DRG']
        super(DrugEvent, self).__init__(patients, indices, split_line)

        # DRG_CODE is the diagnosis billing code for the drug
        self.drg_codes   = (split_line[indices['DRG_TYPE']],
                            split_line[indices['DRG_CODE']])

        self.description = split_line[indices['DESCRIPTION']]

        self.severity    = (split_line[indices['DRG_SEVERITY']],
                            split_line[indices['DRG_MORTALITY']])

        self.admission.drg_events += [self]


    def __str__(self):
        res = self.time + '\t' + 'DRUG Event ' + '\t'
        res += self.description + '\t severity \t' + str(self.severity)
        return res

# PRESCRIPTIONS_DATA_TABLE.csv
class PrescriptionEvent(MimicEvent):


    def __init__(self, patients, mimic_desc, split_line):
        indices         = mimic_desc.indices['PSC']
        super(PrescriptionEvent, self).__init__(patients, indices, split_line)

        self.start_time    = split_line[indices['STARTTIME']]
        self.end_time      = split_line[indices['ENDTIME']]
        if self.start_time != '':
            self.time = self.start_time

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


    def __str__(self):
        res = self.time + '\t' + 'PRESCRIPTION Event ' + '\t'
        res += self.drug_names[0] + '\t' + self.drug_codes[0] + '\t' 
        res += self.drug_info[-1] + '\t NDC \t' + self.drug_codes[-1]
        return res

# PROCEDURES_ICD_DATA_TABLE.csv 
class ProcedureEvent(MimicEvent):


    def __init__(self, patients, mimic_desc, split_line):
        indices         = mimic_desc.indices['PCD']
        super(ProcedureEvent, self).__init__(patients, indices, split_line)

        self.seq_no     = split_line[indices['PROC_SEQ_NUM']]
        self.code       = split_line[indices['ICD9_CODE']]
        
        self.admission.pcd_events += [self]


    def __str__(self):
        res = self.time + '\t' + 'PROCEDURE Event ' + '\t ICD9 \t' + self.code
        return res

# DIAGNOSES_ICD_DATA_TABLE.csv 
class DiagnosisEvent(MimicEvent):


    def __init__(self, patients, mimic_desc, split_line):
        indices         = mimic_desc.indices['DGN']
        super(DiagnosisEvent, self).__init__(patients, indices, split_line)

        self.seq_no     = split_line[indices['SEQUENCE']]
        self.code       = split_line[indices['ICD9_CODE']]
        
        self.admission.dgn_events += [self]


    def __str__(self):
        res = self.time + '\t' + 'DIAGNOSIS Event ' + '\t ICD9 \t' + self.code
        return res


# NOTEEVENTS_DATA_TABLE.csv 
class NoteEvent(MimicEvent):


    def __init__(self, patients, mimic_desc, split_line):
        indices         = mimic_desc.indices['NTE']
        super(NoteEvent, self).__init__(patients, indices, split_line)

        self.date       = split_line[indices['CHARTDATE']]
        if self.date != '':
            self.time = self.date
        self.note_cat   = split_line[indices['CATEGORY']]
        self.note_desc  = split_line[indices['DESCRIPTION']]

        self.care_giver = split_line[indices['CGID']]
        self.erroneous  = split_line[indices['ISERROR']]

        self.note_text  = split_line[indices['TEXT']]
        
        self.admission.nte_events += [self]


    def __str__(self):
        res = self.time + '\t' + 'NOTE Event \t'
        if self.erroneous == '':
            res += self.note_cat + '\t' + self.note_desc + '\t' + self.note_text[:100] + '...'
        else:
            res += 'ERRONEOUS'
        return res
