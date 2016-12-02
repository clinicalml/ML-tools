from MimicDesc import *
from MimicEvent import *

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
            self.dod       = tab[indices[.'DOD']]
        elif len(tab[indices['DOD_HOSP']]) > 0:
            self.dod       = tab[indices['DOD_HOSP']]
        else:
            self.dod       = tab[indices['DOD_SSN']]
        self.expire_flag   = tab[indices['EXPIRE_FLAG']]
        # Maps admission_ids to admission class object 
        self.admissions    = {} 


class MimicAdmGlobal:


    def __init__(self):
        self.admission_time = ''
        self.row_id         = None
        #self.subject_id    = 
        self.admission_id   = None
        self.disch_time     = ''
        self.death_time     = ''
        self.admission_type = ''
        self.admission_loc  = ''
        self.disch_loc      = ''
        self.insurance      = ''
        self.language       = ''
        self.religion       = ''
        self.marital_status = ''
        self.ethnicity      = ''
        self.edreg_time     = ''
        self.edout_time     = ''
        self.diagnosis      = ''
        #self.hosp_exp_flag  = None
        self.has_io_ev_data = None
        self.has_ch_ev_data = None
 

    
class MimicAdmission:


    def __init__(self, line):
        
        self.global_info   = MimicAdmGlobal()
        self.procedures    = []
        self.presriptions  = []
        self.diagnoses     = []
        self.drgs          = []
        self.callout       = ''
        self.services      = []
        self.transferes    = []
        self.cpt           = []
        self.labs          = []
        # TODO

