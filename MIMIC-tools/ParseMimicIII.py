import os
import time
from os.path import join as pjoin

MIMIC_dir = '/data/ml2/jernite/MIMIC3/'


def read_date(stt):
    try:
       return time.strptime(stt, "%Y-%m-%d %H:%M:%S")
    except:
        return stt
    

# The next function parses a string into a string, float or int
def field_eval(st):
    if len(st) > 1:
        if st[0] == '"':
            res = st[1:-1]
        else:
            try:
                res = int(st)
            except:
                try:
                    res = float(st)
                except:
                    res = read_date(st)
        return res
    return ''


# because some of the text fields have commas, splitting a line in the csv
# file into items is a bit tricky (not quite as simple as line.split(','))
def read_csv_line(line):
    res = []
    count = True
    st = ''
    for char in line.strip():
        if char == ',' and count:
            res += [field_eval(st)]
            st = ''
        else:
            if char == '"':
                count = not count
            st += char
    res += [field_eval(st)]
    return res


# We make dictionaries from the corresponding CSV files
dictionaries = {}
dictionary_files = ['D_CPT_DATA_TABLE.csv', 'D_ICD_DIAGNOSES_DATA_TABLE.csv', 
                    'D_ICD_PROCEDURES_DATA_TABLE.csv', 'D_ITEMS_DATA_TABLE.csv',
                    'D_LABITEMS_DATA_TABLE.csv', 'CAREGIVERS_DATA_TABLE.csv']

for dict_file in dictionary_files:
    print dict_file
    dictionaries[dict_file] = {}
    f = open(pjoin(MIMIC_dir, dict_file))
    fields = read_csv_line(f.readline().strip())
    for line in f:
        entry = read_csv_line(line)
        dictionaries[dict_file][entry[1]] = dict(zip(fields, entry))
    f.close()


#####################
#### Treat one batch
#####################


table_files = ['ADMISSIONS_DATA_TABLE.csv', 'DRGCODES_DATA_TABLE.csv',
               'PROCEDURES_ICD_DATA_TABLE.csv', 'CALLOUT_DATA_TABLE.csv',
               'SERVICES_DATA_TABLE.csv','PATIENTS_DATA_TABLE.csv',
               'TRANSFERS_DATA_TABLE.csv', 'DIAGNOSES_ICD_DATA_TABLE.csv',
               'PRESCRIPTIONS_DATA_TABLE.csv']


events_files = ['CPTEVENTS_DATA_TABLE.csv', 'MICROBIOLOGYEVENTS_DATA_TABLE.csv',
                'DATETIMEEVENTS_DATA_TABLE.csv', 'ICUSTAYEVENTS_DATA_TABLE.csv',
                'LABEVENTS_DATA_TABLE.csv', 'CHARTEVENTS_DATA_TABLE.csv',
                'IOEVENTS_DATA_TABLE.csv']


text_files = ['NOTEEVENTS_DATA_TABLE.csv']

headers = {}
for file_name in table_files + events_files + text_files:
    f = open(pjoin(MIMIC_dir, file_name))
    headers[file_name] = read_csv_line(f.readline().strip())
    f.close()


batch_dir = pjoin(MIMIC_dir, 'Parsed/MIMIC3_split/%02d' % (0,))

notes = {}
# Start with the text notes:
f = open(pjoin(batch_dir, 'NOTEEVENTS_DATA_TABLE.csv'))
header = headers['NOTEEVENTS_DATA_TABLE.csv'][:-1]
for line in f:
    if line.strip() == '<VISIT>':
        st = []
    elif line.strip() == '</VISIT>':
        visit = dict(zip(header, read_csv_line(st[0][:-2])))
        visit['TEXT'] = '\n'.join(st[1:])
        notes[visit['SUBJECT_ID']] = notes.get(visit['SUBJECT_ID'], {})
        notes[visit['SUBJECT_ID']][visit['HADM_ID']] = notes[visit['SUBJECT_ID']].get(visit['HADM_ID'], []) + [visit]
        continue
    else:
        st += [line.strip()]

f.close()


def file_to_dict(file_name):
    patients = {}
    f = open(pjoin(batch_dir, file_name))
    header = headers[file_name]
    for line in f:
        if len(line.strip()) > 0:
            visit = dict(zip(header, read_csv_line(line.strip())))
            patients[visit['SUBJECT_ID']] = patients.get(visit['SUBJECT_ID'], []) + [visit]
    return patients


def add_info(patients, new_dic, dic_name):
    for pid, info_list in new_dic.items():
        if pid != '':
            patients[pid] = patients.get(pid, {})
            for info in info_list:
                patients[pid]['ADMISSIONS'][info['HADM_ID']] = patients[pid]['ADMISSIONS'].get(info['HADM_ID'], {})
                patients[pid]['ADMISSIONS'][info['HADM_ID']][dic_name] = patients[pid]['ADMISSIONS'][info['HADM_ID']].get(dic_name, []) + [info]



patients = file_to_dict('PATIENTS_DATA_TABLE.csv')
admissions = file_to_dict('ADMISSIONS_DATA_TABLE.csv')
for pid in patients:
    if pid != '':
        admission_list = sorted(admissions[pid], key=lambda x:x['ADMITTIME'])
        for admission in admission_list:
            admission['NOTES'] = notes.get(pid, {}).get(admission['HADM_ID'], [])
        patients[pid] = patients[pid][0]
        patients[pid]['ADMISSIONS'] = dict([(ad['HADM_ID'], ad) for ad in admission_list])


# After reading PATIENTS_DATA_TABLE, NOTEEVENTS_DATA_TABLE, and ADMISSIONS_DATA_TABLE,
# an admission item looks like this (for patient 16, admission 103251):
# sorted(patients[16]['ADMISSIONS'][103251].keys())
# ['ADMISSION_LOCATION', 'ADMISSION_TYPE', 'ADMITTIME', 'DEATHTIME',
# 'DIAGNOSIS', 'DISCHARGE_LOCATION', 'DISCHTIME', 'ETHNICITY', 'HADM_ID',
# 'HAS_CHARTEVENTS_DATA', 'HAS_IOEVENTS_DATA', 'INSURANCE', 'LANGUAGE',
# 'MARITAL_STATUS', 'NOTES', 'RELIGION', 'ROW_ID', 'SUBJECT_ID']
#
# We are going to add fields from other files
# Tables are described in: https://mimic.physionet.org/mimictables/admissions/


# DRG: Contains diagnosis related groups (DRG) codes for patients
drgs = file_to_dict('DRGCODES_DATA_TABLE.csv')
add_info(patients, drgs, 'DRG')

# PROCEDURES: Contains ICD procedures for patients, most notably ICD-9
# procedures
procedures = file_to_dict('PROCEDURES_ICD_DATA_TABLE.csv')
add_info(patients, procedures, 'PROCEDURES')

# CALLOUT: Provides information when a patient was READY for discharge
# from the ICU, and when the patient was actually discharged
callout = file_to_dict('CALLOUT_DATA_TABLE.csv')
add_info(patients, callout, 'CALLOUT')

# SERVICES: Lists services that a patient was admitted/transferred under
services = file_to_dict('SERVICES_DATA_TABLE.csv')
add_info(patients, services, 'SERVICES')

# TRANSFERS: Physical locations for patients throughout their hospital stay
transfers = file_to_dict('TRANSFERS_DATA_TABLE.csv')
add_info(patients, transfers, 'TRANSFERS')

# DIAGNOSES: Physical locations for patients throughout their hospital stay
diagnoses = file_to_dict('DIAGNOSES_ICD_DATA_TABLE.csv')
add_info(patients, diagnoses, 'DIAGNOSES')

# PRESCRIPTIONS: Contains medication related order entries, i.e. prescriptions.
prescriptions = file_to_dict('PRESCRIPTIONS_DATA_TABLE.csv')
add_info(patients, prescriptions, 'PRESCRIPTIONS')

# CPT: Contains current procedural terminology (CPT) codes, which 
#facilitate billing for procedures performed on patients.
cpt = file_to_dict('CPTEVENTS_DATA_TABLE.csv')
add_info(patients, cpt, 'CPT')

# MICROBIOLOGY: Contains microbiology information, including tests
# performed and sensitivities.
microbiology = file_to_dict('MICROBIOLOGYEVENTS_DATA_TABLE.csv')
add_info(patients, microbiology, 'MICROBIOLOGY')

# TIMELINE: Contains all date formatted data.
datetime = file_to_dict('DATETIMEEVENTS_DATA_TABLE.csv')
add_info(patients, datetime, 'TIMELINE')

# ICU_STAYS: Defines each ICUSTAY_ID in the database, i.e. defines a
#  single ICU stay.
icu = file_to_dict('ICUSTAYEVENTS_DATA_TABLE.csv')
add_info(patients, icu, 'ICU_STAYS')

# LABS: Contains all laboratory measurements for a given patient,
# including out patient data.
labs = file_to_dict('LABEVENTS_DATA_TABLE.csv')
add_info(patients, labs, 'LABS')

# IOEVENTS: Input/output data for patients.
ioevents = file_to_dict('IOEVENTS_DATA_TABLE.csv')
add_info(patients, ioevents, 'IOEVENTS')


# CHARTEVENTS is huge and not necessarily useful...
# CHARTEVENTS: Contains all charted data for all patients.
# chart = file_to_dict('CHARTEVENTS_DATA_TABLE.csv')


patient_locations = ['CALLOUT', 'SERVICES', 'TRANSFERS', 'ICU']

general_fields = ['HADM_ID',
                  'ADMISSION_TYPE', 'ADMITTIME', 'ADMISSION_LOCATION',
                  'DISCHARGE_LOCATION', 'DISCHTIME',
                  'CPT', 'DIAGNOSES', 'DIAGNOSIS', 'DEATHTIME',
                  'INSURANCE', 'MARITAL_STATUS', 'RELIGION', 'LANGUAGE']

timed_fields = ['PROCEDURES', 'NOTES', 'LABS', 'PRESCRIPTIONS']

useless_fields = ['ROW_ID', 'HAS_IOEVENTS_DATA', 'SUBJECT_ID', 'HAS_CHARTEVENTS_DATA']

others = ['ETHNICITY']


def make_admission_record(admission):
    adm_record = {}
    adm_record['ADMISSION_INFO'] = {}
    for k in general_fields:
        adm_record['ADMISSION_INFO'][k] = admission[k]
    return adm_record


def print_patient_record(patient):
    record = {}
    record['PATIENT_INFO'] = {}
    # DOD, combines DOD_HOSP and DOD_SSN, ROW_ID is useless
    print "*************** PATIENT INFO ***************"
    print 'SUBJECT_ID', '\t', patient['SUBJECT_ID']
    print 'GENDER', '\t\t', patient['GENDER']
    print 'DOB', '\t\t', time.strftime('%m/%d/%Y at %H:%M:%S', patient['DOB'])
    print 'DOD', '\t\t', time.strftime('%m/%d/%Y at %H:%M:%S', patient['DOD'])
    print 'DIED', '\t\t', patient['HOSPITAL_EXPIRE_FLAG']
    pt_admissions = sorted(patient['ADMISSIONS'].values(), key=lambda x:['ADMITTIME'])
    for i, admission in enumerate(pt_admissions):
        print "--------------- VISIT %d -----------" % (i,)
        print 'TYPE', '\t\t', admission['ADMISSION_TYPE']


#####################
#### ICD9
#####################

icd9_dic = {}

f = open('icd9.csv')
for line in f:
    st = line.strip().split(',')
    icd9_dic[st[0]] = (st[1], st[2])

f.close()

def icd9_lookup(st):
    try:
        return (st, icd9_dic[st][0], icd9_dic[st][1])
    except:
        pass
    for i in range(len(st), 1, -1):
        try:
            stb = st[:i] + '.' + st[i:]
            return (stb, icd9_dic[stb][0], icd9_dic[stb][1])
        except:
            pass
    return (st, 'not found', 'na')


#############
patient = patients[518]
print_patient_record(patient)
pt_admissions = sorted(patient['ADMISSIONS'].values(), key=lambda x:['ADMITTIME'])
