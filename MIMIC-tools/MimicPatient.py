from MimicDesc import *
from MimicEvent import *

class MimicAdmission:


    def __init__(self, patients, mimic_desc, split_line):
        indices         = mimic_desc.indices['ADM']
        self.patient_id = split_line[indices['SUBJECT_ID']]
        try:
            self.patient    = patients[self.patient_id]
        except:
            print 'ERROR--------', '\t', 'PATIENT NOT FOUND', self.patient_id

        self.admission_id    = split_line[indices['HADM_ID']]

        self.in_time    = split_line[indices['ADMITTIME']]
        self.out_time   = split_line[indices['DISCHTIME']]
        self.death_time = split_line[indices['DEATHTIME']]

        self.adm_type   = split_line[indices['ADMISSION_TYPE']] 
        self.in_loc     = split_line[indices['ADMISSION_LOCATION']]
        self.out_loc    = split_line[indices['DISCHARGE_LOCATION']]

        self.language   = split_line[indices['LANGUAGE']]
        self.religon    = split_line[indices['RELIGION']]
        self.married    = split_line[indices['MARITAL_STATUS']]
        self.ethnicity  = split_line[indices['ETHNICITY']]

        self.diagnosis  = split_line[indices['DIAGNOSIS']]
        
        self.cpt_events = []
        self.icu_events = []
        self.lab_events = []
        self.mic_events = []
        self.drg_events = []
        self.psc_events = []
        self.pcd_events = []
        self.nte_events = []

        self.patient.admissions[self.admission_id] = self

class MimicPatient:


    def __init__(self, mimic_desc, split_line):
        indices             = mimic_desc.indices['PTT']
        self.patient_id     = split_line[indices['SUBJECT_ID']]

        self.gender         = split_line[indices['GENDER']]

        self.dob            = split_line[indices['DOB']]
        self.dod            = ''
        if len(split_line[indices['DOD']]) > 0:
            self.dod        = split_line[indices['DOD']]
        elif len(split_line[indices['DOD_HOSP']]) > 0:
            self.dod        = split_line[indices['DOD_HOSP']]
        else:
            self.dod        = split_line[indices['DOD_SSN']]
        self.expire_flag    = split_line[indices['HOSPITAL_EXPIRE_FLAG']]

        # Maps admission_ids to admission class object
        self.admissions     = {}
