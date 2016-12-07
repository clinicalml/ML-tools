from MimicDesc import *

class MimicAdmission:


    def __init__(self, patients, mimic_desc=None, split_line=None,
                 patient_id=None, admission_id=None):
        if patient_id == None:
            indices         = mimic_desc.indices['ADM']

            self.patient_id = split_line[indices['SUBJECT_ID']]
            self.admission_id    = split_line[indices['HADM_ID']]

            self.in_time    = split_line[indices['ADMITTIME']]
            self.out_time   = split_line[indices['DISCHTIME']]
            self.death_time = split_line[indices['DEATHTIME']]

            self.adm_type   = split_line[indices['ADMISSION_TYPE']] 
            self.in_loc     = split_line[indices['ADMISSION_LOCATION']]
            self.out_loc    = split_line[indices['DISCHARGE_LOCATION']]

            self.language   = split_line[indices['LANGUAGE']]
            self.religion   = split_line[indices['RELIGION']]
            self.married    = split_line[indices['MARITAL_STATUS']]
            self.ethnicity  = split_line[indices['ETHNICITY']]

            self.diagnosis  = split_line[indices['DIAGNOSIS']]
        else:
            self.patient_id     = patient_id
            self.admission_id   = admission_id
            self.in_time        = '0001-01-01 00:00:00'
            self.out_time       = '0001-01-01 00:00:00'
        
        try:
            self.patient    = patients[self.patient_id]
        except:
            print 'ERROR--------', '\t', 'PATIENT NOT FOUND', self.patient_id
        
        self.cpt_events = []
        self.icu_events = []
        self.lab_events = []
        self.mic_events = []
        self.drg_events = []
        self.psc_events = []
        self.pcd_events = []
        self.nte_events = []
        self.dgn_events = []

        self.patient.admissions[self.admission_id] = self


    def __str__(self, max_n=5):
        res = self.in_time + '\t ADMISSION \t' + self.admission_id + '\n'
        res += self.adm_type + '\t IN \t' + self.in_loc + '\t OUT \t' + self.out_loc  + '\n'
        res += 'LANG \t' + self.language + '\t REL \t' + self.religion  + '\t'
        res += 'MARRIED \t' + self.married + '\t ETHNO \t' + self.ethnicity  + '\n'
        res += '----- CPT EVENTS \n'
        for evt in sorted(self.cpt_events, key=lambda x:x.time)[:max_n]:
            res += str(evt) + '\n'
        res += '----- ICU ADMISSIONS \n'
        for evt in sorted(self.icu_events, key=lambda x:x.time)[:max_n]:
            res += str(evt) + '\n'
        res += '----- LABS \n'
        for evt in sorted(self.lab_events, key=lambda x:x.time)[:max_n]:
            res += str(evt) + '\n'
        res += '----- MICROBIOLOGY \n'
        for evt in sorted(self.mic_events, key=lambda x:x.time)[:max_n]:
            res += str(evt) + '\n'
        res += '----- DRUGS \n'
        for evt in sorted(self.drg_events, key=lambda x:x.time)[:max_n]:
            res += str(evt) + '\n'
        res += '----- PRESCRIPTIONS \n'
        for evt in sorted(self.psc_events, key=lambda x:x.time)[:max_n]:
            res += str(evt) + '\n'
        res += '----- PROCEDURES \n'
        for evt in sorted(self.pcd_events, key=lambda x:x.time)[:max_n]:
            res += str(evt) + '\n'
        res += '----- NOTES \n'
        for evt in sorted(self.nte_events, key=lambda x:x.time)[:max_n]:
            res += str(evt) + '\n'
        res += '----- DIAGNOSES \n'
        for evt in sorted(self.dgn_events, key=lambda x:x.time)[:max_n]:
            res += str(evt) + '\n'
        return res

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
