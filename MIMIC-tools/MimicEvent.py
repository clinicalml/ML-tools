from MimicDesc import *

class MimicEvent:


    def __init__(self, patient, admission,
                 event_id=None, start_time=None, end_time=None):
        self.patient     = patient
        self.admission   = admission
        self.indices     = self.patient.mimic_desc.indices
        
        self.start_time  = start_time
        self.end_time    = end_time

# ICUSTAYEVENTS_DATA_TABLE.csv
class IcuEvent(MimicEvent):


    def __init__(self, patient, admission, line):
        super(MimicEvent, self).__init__(patient, admission)
        indices         = self.indices['ICU']
        split_line      = line.strip().split(',')
             
        self.start_time = split_line[indices['INTIME']]
        self.end_time   = split_line[indices['OUTIME']]
        self.icu_id     = split_line[indices['ICUSTAY_ID']
        self.info       = (split_line[indices['FIRST_CAREUNIT']],
                           split_line[indices['LAST_CAREUNIT']])
        
# CPTEVENTS_DATA_TABLE.csv
class CptEvent(MimicEvent):
    
    def __init__(self, patient, admission, line):
        super(MimicEvent, self).__init__(patient, admission)
        split_line      = line.strip().split(',')
        indices         = self.indices['CPT']
        
        self.date       = split_line[indices['CHARTDATE']]
        
        self.info       = (split_line[indices['SECTIONHEADER']], 
                           split_line[indices['SUBSECTIONHEADER']],
                           split_line[indices['DESCRIPTION']])
        self.codes      = (split_line[indices['CPT_CD']], split_line[indices['CPT_NUMBER']], split_line[indices['CPT_SUFFIX']])
        
# LABEVENTS_DATA_TABLE.csv
class LabEvent(MimicEvent):
    
    def __init__(self, patient, admission, line):
        super(MimicEvent, self).__init__(patient, admission) 
        split_line      = line.strip().split(',')
        indices         = self.indices['LAB']
        self.start_time = split_line[indices['CHARTTIME']]
        self.end_time   = split_line[indices['CHARTTIME']]
        
        self.lab_id     = split_line[indices['ITEMID']]
                                     
        self.value      = (split_line[indices['VALUE']],
                           split_line[indices['VALUENUM']],
                           split_line[indices['VALUEOM']])
        self.flag       = split_line[indices['FLAG']]]
       
        
# MICROBIOLOGYEVENTS_DATA_TABLE.csv
class MicroEvent(MimicEvent):
    
    def __init__(self, patient, admission, line):
        super(MimicEvent, self).__init__(patient, admission) 
    split_line    = line.strip().split(',')
    indices       = self.indices['MICROBIO']
    
    self.date            = split_line[indices['CHARTDATE']]
    self.start_time      = split_line[indices['CHARTTIME']]
    self.end_time        = split_line[indices['CHARTTIME']]
    
    self.item_id         = split_line[indices['SPEC_ITEMID']]
    self.code            = split_line[indices['SPEC_TYPE_CD']] 
    self.description     = split_line[indices['SPEC_TYPE_DESC']]]
    
    self.dilution        = (split_line[indices['DILUTION_TEXT']], 
                            split_line[indices['DILUTION_COMPARISON']],
                            split_line[indices['DILUTION_VALUE']])

    self.interpretation   = split_line[indices['INTERPRETATION']]

# DRGCODES_DATA_TABLE.csv
class DrugEvent(MimicEvent):
    
    
    def __init__(self, patient, admission, line):
        super(MimicEvent, self).__init__(patient, admission)
        
        split_line       = line.strip().split(',')
        indices          = self.indices['DRG']
        
        self.drg_code    = (split_line[indices['DRG_TYPE']], 
                            split_line[indices['DRG_CODE']])
                            
        self.description = split_line[indices['DESCRIPTION']]
        
        self.severity    = (split_line[indices['DRG_SEVERITY']], 
                            split_line[indices['DRG_MORTALITY']])
        

# PRESCRIPTIONS_DATA_TABLE.csv
class PrescriptionEvent(MimicEvent):
    
    
    def __init__(self, patient, admission, line):
        super(MimicEvent, self).__init__(patient, admission) 
        
        split_line = line.strip().split(',')
        indices = self.indices['PSC']
        
        self.start_time    = split_line[indices['STARTTIME']]
        self.end_time      = split_line[indices['ENDTIME']]
        
        self.icu_id        = split_line[indices['ICUSTAY_ID']]
        
        self.drug_type     = split_line[indices['DRUG_TYPE']]
        self.drug_names    = (split_line[indices['DRUG']], split_line[indices['DRUG_NAME_POE']], 
                                  split_line[indices['DRUG_NAME_GENERIC']])
                              
        self.drug_codes    = (split_line[indices['FORMULARY_DRUG_CD']], split_line[indices['GSN']], 
                                  split_line[indices['NDC']])
        
        self.drug_info     = (split_line[indices['PROD_STRENGTH']], split_line[indices['DOSE_VAL_RX']],         split_line[indices['DOSE_UNIT_RX']], split_line[indices['FORM_VAL_DISP']], split_line[indices['FORM_UNIT_DISP']], split_line[indices['ROUTE']])
        

# PROCEDURES_ICD_DATA_TABLE.csv 
class ProcedureEvent(MimicEvent):
    
    
    def __init__(self, patient, admission, line):
        super(MimicEvent, self).__init__(patient, admission)
        # TODO


# NOTEEVENTS_DATA_TABLE.csv 
class NoteEvent(MimicEvent):
    
    
    def __init__(self, patient, admission, line):
        super(MimicEvent, self).__init__(patient, admission)
        # TODO

