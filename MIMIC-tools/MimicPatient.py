from MimicDesc import *
from MimicEvent import *

class MimicAdmission():
    def __init__(self, patient line):
    self.patient      = patient
    split_line        = line.strip().split(',')
    
    indices           = self.indices['ADMIN']      
    self.patient_id   = split_line[indices['SUBJECT_ID']]
    self.admission_id = split_line[indices['HADM_ID']]
    self.times        = (split_line[indices['CHARTDATE']], split_line[indices['CHARTTIME']]) 

         

class MimicPatient:

    def __init__(self, line, mimic_desc):
        self.mimic_desc    = mimic_desc
        
        tab                = line.strip().split(',')
        indices            = mimic_desc.indices['PATIENT']
        
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


