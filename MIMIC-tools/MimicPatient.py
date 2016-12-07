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


    def __str__(self):
        res = '---------------- PATIENT \t' + self.patient_id + '\n'
        res += '--GENDER-- ' + self.gender
        res += '\t --DOB-- ' + self.dob
        res += '\t --DOD-- ' + self.dod
        res += '\t --Hosp_EXPIRED-- ' + self.expire_flag + '\n'
        res += '---------------- ADMISSIONS \t' + str(len(self.admissions)) + '\n'
        admissions = sorted(self.admissions.items(), key=lambda x:x[1].in_time)
        for adm_id, adm in admissions:
            res += '----ADMISSION-- ' + adm_id
            res += '\t --START-- ' + adm.in_time
            res += '\t --END-- ' + adm.out_time + '\n'
            res += str(len(adm.cpt_events)) + ' CPT EVENTS \t'
            res += str(len(adm.icu_events)) + ' ICU STAYS \t'
            res += str(len(adm.lab_events)) + ' LABS \t'
            res += str(len(adm.mic_events)) + ' MICROBIOLOGY \t'
            res += str(len(adm.drg_events)) + ' DRUGS BILLED \n'
            res += str(len(adm.psc_events)) + ' PRESCRIPTIONS \t'
            res += str(len(adm.pcd_events)) + ' PROCEDURES \t'
            res += str(len(adm.dgn_events)) + ' DIAGNOSES \t'
            res += str(len(adm.nte_events)) + ' NOTES\n'
            res += '-------------- \n'
        return res

