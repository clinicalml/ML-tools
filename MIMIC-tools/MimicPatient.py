from MimicDesc import *
from MimicEvent import *

class MimicAdmission:
    
    
    def __init__(self, patient line):
    self.patient         = patient
    split_line           = line.strip().split(',')
    indices              = self.pateint.mimic_desc.indices['ADMISSION']
    
    self.patient_id      = split_line[indices['SUBJECT_ID']] 
    self.admission_id    = split_line[indices['HADM_ID']] 
    
    self.times           = (split_line[indices['ADMITTIME']],
                            split_line[indices['DISCHTIME']],
                            split_line[indices['DEATHTIME']] )
               
    self.admission_type  = split_line[indices['ADMISSION_TYPE']] 
    self.location        = (split_line[indices['ADMISSION_LOCATION']],  split_line[indices['DISCHARGE_LOCATION']])
          
    self.language        = split_line[indices['LANGUAGE']]
    self.religon         = split_line[indices['RELIGION']]
    self.marital_status  = split_line[indices['MARITAL_STATUS']]
    self.ethnicity       = split_line[indices['ETHNICITY']]
    
    self.diagnosis       = split_line[indices['DIAGNOSIS']]
    self.expire_flag     = split_line[indices['HOSPITAL_EXPIRE_FLAG']]


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
        self.expire_flag   = tab[indices['HOSPITAL_EXPIRE_FLAG']]
        # Maps admission_ids to admission class object 
        self.admissions    = {} 


