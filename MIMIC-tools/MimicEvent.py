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
        # 'INTIME', 'OUTTIME', 'LOS' -> self.start_time, self.end_time
        # 'ICUSTAY_ID' -> self.event_id
        # 'FIRST_CAREUNIT', 'LAST_CAREUNIT' -> self.info
        
        indices         = self.indices['ICU']
        split_line      = line.strip().split(',')
             
        self.start_time = split_line[indices['INTIME']]
        self.end_time   = split_line[indices['OUTIME']]
        self.icu_id     = split_line[indices['ICUSTAY_ID']
        self.info       = (split_line[indices['FIRST_CAREUNIT']], split_line[indices['LAST_CAREUNIT']])
        
# CPTEVENTS_DATA_TABLE.csv
class CptEvent(MimicEvent):
    
    def __init__(self, patient, admission, line):
        super(MimicEvent, self).__init__(patient, admission) 
        
        # 'CHARTDATE' -> self.start_time, self.end_time
        # 'SECTIONHEADER', 'SUBSECTIONHEADER', 'DESCRIPTION' -> self.info 
        # 'CPT_CD', 'CPT_NUMBER', 'CPT_SUFFIX' -> self.codes
        split_line      = line.strip().split(',')
        indices         = self.indices['CPT']
        self.start_time = split_line[indices['CHARTDATE']]
        self.end_time   = split_line[self.start_time]
        self.info       = (split_line[indices['SECTIONHEADER']], 
                            split_line[indices['SUBSECTIONHEADER']], split_line[indices['DESCRIPTION']])
        self.codes      = (split_line[indices['CPT_CD']], split_line[indices['CPT_NUMBER']], split_line[indices['CPT_SUFFIX']])
        
# LABEVENTS_DATA_TABLE.csv
class LabEvent(MimicEvent):
    
    def __init__(self, patient, admission, line):
        super(MimicEvent, self).__init__(patient, admission) 
        split_line    = line.strip().split(',')
        indices       = indices['LAB']
        self.value    = (split_line[indices['VALUE']], split_line[indices['VALUENUM']], split_line[indices['VALUEOM']])
        self.flag     = split_line[indices['FLAG']]]
       
        
# MICROBIOLOGYEVENTS_DATA_TABLE.csv
class MicroEvent(MimicEvent):
    
    def __init__(self, patient, admission, line):
        super(MimicEvent, self).__init__(patient, admission) 
    split_line    = line.strip().split(',')
    indices       = self.indices['MICROBIO']
    #specITEMID, SPEC_TYPE_CD, SPEC_TYPE_DESC
    self.specs            = (split_line[indices['specITEMID']], 
                                split_line[indices['SPEC_TYPE_CD']], split_line[indices['SPEC_TYPE_DESC']]])
    self.orgs             = (split_line[indices['ORG_IT']], 
                                split_line[indices['ORG_CD']], split_line[indices['ORG_NAME']])
    self.isolate_num      = split_line[indices['ISOLATE_NUM']]
    
    #Ab_itemid, AB_CD, AB_NAME
    self.abs              = (split_line[indices['AB_itemid']], split_line[indices['AB_CD']], split_line[indices['AB_NAME']])
    #dilution_text, dilution_comparison, dilution_value 
    self.dilutions        = (split_line[indices['dilution_text']], 
                                split_line[indices['dilution_comparison']], split_line[indices['dilution_value']])
    self.interpretation   = split_line[indices['INTERPRETATION']]

# DRGCODES_DATA_TABLE.csv
class DrugEvent(MimicEvent):
    
    
    def __init__(self, patient, admission, line):
        super(MimicEvent, self).__init__(patient, admission)
        
        split_line = line.strip().split(',')
        indices    = self.indices['DRG']
        
        self.drg_code    = (split_line[indices['DRG_TYPE']], split_line[indices['DRG_CODE']])
        self.description = split_line[indices['DESCRIPTION']]
        self.severity    = (split_line[indices['DRG_SEVERITY']], split_line[indices['DRG_MORTALITY']])
        

# PRESCRIPTIONS_DATA_TABLE.csv
class PrescriptionEvent(MimicEvent):
    
    
    def __init__(self, patient, admission, line):
        super(MimicEvent, self).__init__(patient, admission) 

# PROCEDURES_ICD_DATA_TABLE.csv 
class ProceduresEvent(MimicEvent):
    
    
    def __init__(self, patient, admission, line):
        super(MimicEvent, self).__init__(patient, admission) 

# NOTEEVENTS_DATA_TABLE.csv 
class NoteEvent(MimicEvent):
    
    
    def __init__(self, patient, admission, line):
        super(MimicEvent, self).__init__(patient, admission) 

