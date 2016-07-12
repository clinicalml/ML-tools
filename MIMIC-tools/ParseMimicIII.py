import os
import time
import cPickle as pickle
import multiprocessing
import traceback
from multiprocessing import Pool
from os.path import join as pjoin

MIMIC_dir = '/data/ml2/jernite/MIMIC3'
Out_dir = '/data/ml2/ankit/MIMIC3pk'


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


def file_to_dict(batch_dir, file_name, headers):
    patients = {}
    try:
        f = open(pjoin(batch_dir, file_name))
        header = headers[file_name]
        for line in f:
            if len(line.strip()) > 0:
                visit = dict(zip(header, read_csv_line(line.strip())))
                patients[visit['SUBJECT_ID']] = patients.get(visit['SUBJECT_ID'], []) + [visit]
    except IOError:
        pass
    return patients


def add_info(patients, new_dic, dic_name):
    print dic_name
    for pid, info_list in new_dic.items():
        if pid != '':
            patients[pid] = patients.get(pid, {})
            for info in info_list:
                patients[pid]['ADMISSIONS'][info['HADM_ID']] = patients[pid]['ADMISSIONS'].get(info['HADM_ID'], {})
                patients[pid]['ADMISSIONS'][info['HADM_ID']][dic_name] = patients[pid]['ADMISSIONS'][info['HADM_ID']].get(dic_name, []) + [info]


def make_headers():
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
    return headers


def save_dictionaries():
    # We make dictionaries from the corresponding CSV files
    dictionaries = {}
    #dictionary_files = ['D_CPT_DATA_TABLE.csv', 'D_ICD_DIAGNOSES_DATA_TABLE.csv', 
    #                    'D_ICD_PROCEDURES_DATA_TABLE.csv', 'D_ITEMS_DATA_TABLE.csv',
    #                    'D_LABITEMS_DATA_TABLE.csv', 'CAREGIVERS_DATA_TABLE.csv']
    dictionary_files = ['D_ICD_DIAGNOSES_DATA_TABLE.csv',
                        'D_ICD_PROCEDURES_DATA_TABLE.csv',
                        'D_LABITEMS_DATA_TABLE.csv']

    for dict_file in dictionary_files:
        print dict_file
        dictionaries[dict_file] = {}
        f = open(pjoin(MIMIC_dir, dict_file))
        fields = read_csv_line(f.readline().strip())
        for line in f:
            entry = read_csv_line(line)
            dictionaries[dict_file][entry[1]] = dict(zip(fields, entry))
        f.close()

    if dictionaries:
        with open(pjoin(Out_dir, 'dicts.pk'), 'wb') as f:
            pickle.dump(dictionaries, f, -1)


def save_split(split, headers):
    print 'Split', split
    batch_dir = pjoin(MIMIC_dir, 'Parsed/MIMIC3_split/%02d' % (split,))

    notes = {}
    #print 'NOTEEVENTS'
    #f = open(pjoin(batch_dir, 'NOTEEVENTS_DATA_TABLE.csv'))
    #header = headers['NOTEEVENTS_DATA_TABLE.csv'][:-1]
    #st = []
    #nextst = []
    #done = False
    #for line in f:
    #    if line.strip() == '</VISIT>' or done:
    #        done = True
    #        while done:
    #            visit = dict(zip(header, read_csv_line(st[0][:-2])))
    #            visit['TEXT'] = '\n'.join(st[1:])
    #            notes[visit['SUBJECT_ID']] = notes.get(visit['SUBJECT_ID'], {})
    #            notes[visit['SUBJECT_ID']][visit['HADM_ID']] = notes[visit['SUBJECT_ID']].get(visit['HADM_ID'], []) + [visit]
    #            st = nextst
    #            nextst = []
    #            if line.strip() == '</VISIT>' and st:
    #                done = True
    #            else:
    #                done = False
    #    elif line.strip() != '<VISIT>':
    #        content = line.strip()
    #        if st and '"' in content:
    #            nextcontent = content[:content.find('"')]
    #            nextl = content[content.find('"')+1:].strip()
    #            if nextl:
    #                nextl = nextl.split(',', 9)
    #                nextst = [','.join(nextl[:9])]
    #                if nextl[9:]:
    #                    nextst += nextl[9:]
    #            done = True
    #            st += [nextcontent]
    #        elif not st:
    #            content = content.split(',', 9)
    #            st = [','.join(content[:9])]
    #            if content[9:]:
    #                st += content[9:]
    #        else:
    #            st += [content]
    #f.close()

    patients = file_to_dict(batch_dir, 'PATIENTS_DATA_TABLE.csv', headers)
    admissions = file_to_dict(batch_dir, 'ADMISSIONS_DATA_TABLE.csv', headers)
    print 'PATIENTS and ADMISSIONS'
    for pid in patients:
        if pid != '':
            admission_list = sorted(admissions[pid], key=lambda x:x['ADMITTIME'])
            for admission in admission_list:
                admission['NOTES'] = notes.get(pid, {}).get(admission['HADM_ID'], [])
            patients[pid] = patients[pid][0]
            patients[pid]['ADMISSIONS'] = dict([(ad['HADM_ID'], ad) for ad in admission_list])

    # DRG: Contains diagnosis related groups (DRG) codes for patients
    #drgs = file_to_dict(batch_dir, 'DRGCODES_DATA_TABLE.csv', headers)
    #add_info(patients, drgs, 'DRG')

    # PROCEDURES: Contains ICD procedures for patients, most notably ICD-9
    # procedures
    procedures = file_to_dict(batch_dir, 'PROCEDURES_ICD_DATA_TABLE.csv', headers)
    add_info(patients, procedures, 'PROCEDURES')

    # CALLOUT: Provides information when a patient was READY for discharge
    # from the ICU, and when the patient was actually discharged
    #callout = file_to_dict(batch_dir, 'CALLOUT_DATA_TABLE.csv', headers)
    #add_info(patients, callout, 'CALLOUT')

    # SERVICES: Lists services that a patient was admitted/transferred under
    #services = file_to_dict(batch_dir, 'SERVICES_DATA_TABLE.csv', headers)
    #add_info(patients, services, 'SERVICES')

    # TRANSFERS: Physical locations for patients throughout their hospital stay
    #transfers = file_to_dict(batch_dir, 'TRANSFERS_DATA_TABLE.csv', headers)
    #add_info(patients, transfers, 'TRANSFERS')

    # DIAGNOSES: Physical locations for patients throughout their hospital stay
    diagnoses = file_to_dict(batch_dir, 'DIAGNOSES_ICD_DATA_TABLE.csv', headers)
    add_info(patients, diagnoses, 'DIAGNOSES')

    # PRESCRIPTIONS: Contains medication related order entries, i.e. prescriptions.
    prescriptions = file_to_dict(batch_dir, 'PRESCRIPTIONS_DATA_TABLE.csv', headers)
    add_info(patients, prescriptions, 'PRESCRIPTIONS')

    # CPT: Contains current procedural terminology (CPT) codes, which 
    #facilitate billing for procedures performed on patients.
    #cpt = file_to_dict(batch_dir, 'CPTEVENTS_DATA_TABLE.csv', headers)
    #add_info(patients, cpt, 'CPT')

    # MICROBIOLOGY: Contains microbiology information, including tests
    # performed and sensitivities.
    #microbiology = file_to_dict(batch_dir, 'MICROBIOLOGYEVENTS_DATA_TABLE.csv', headers)
    #add_info(patients, microbiology, 'MICROBIOLOGY')

    # TIMELINE: Contains all date formatted data.
    #datetime = file_to_dict(batch_dir, 'DATETIMEEVENTS_DATA_TABLE.csv', headers)
    #add_info(patients, datetime, 'TIMELINE')

    # ICU_STAYS: Defines each ICUSTAY_ID in the database, i.e. defines a
    #  single ICU stay.
    icu = file_to_dict(batch_dir, 'ICUSTAYEVENTS_DATA_TABLE.csv', headers)
    add_info(patients, icu, 'ICU_STAYS')

    # LABS: Contains all laboratory measurements for a given patient,
    # including out patient data.
    labs = file_to_dict(batch_dir, 'LABEVENTS_DATA_TABLE.csv', headers)
    add_info(patients, labs, 'LABS')

    # IOEVENTS: Input/output data for patients.
    #ioevents = file_to_dict(batch_dir, 'IOEVENTS_DATA_TABLE.csv', headers)
    #add_info(patients, ioevents, 'IOEVENTS')

    # CHARTEVENTS is huge and not necessarily useful...
    # CHARTEVENTS: Contains all charted data for all patients.
    # chart = file_to_dict(batch_dir, 'CHARTEVENTS_DATA_TABLE.csv', headers)

    procedures = set()
    diagnoses = set()
    labs = set()
    prescriptions = set()
    if patients:
        with open(pjoin(Out_dir, 'patients_%02d.pk' % (split,)), 'wb') as f:
            pickle.dump(patients, f, -1)
        print 'Building vocab for split', split
        for patient in patients.values():
            if isinstance(patient, dict):
                for admission in patient.get('ADMISSIONS', {}).values():
                    for procedure in admission.get('PROCEDURES', []):
                        procedures.add(procedure.get('ICD9_CODE', ''))
                    for diagnosis in admission.get('DIAGNOSES', []):
                        diagnoses.add(diagnosis.get('ICD9_CODE', ''))
                    for lab in admission.get('LABS', []):
                        labs.add(lab.get('ITEMID', ''))
                    for prescription in admission.get('PRESCRIPTIONS', []):
                        prescriptions.add(prescription.get('NDC', ''))
    return (procedures, diagnoses, labs, prescriptions)


class SaveSplit(object):
    def __init__(self, headers):
        self.headers = headers
    def __call__(self, split):
        try:
            return save_split(split, self.headers)
        except:
            print traceback.print_exc(10)


print 'headers'
headers = make_headers()
print 'dicts'
save_dictionaries()

print 'patients'
p = Pool(int(.5 + (.9 * float(multiprocessing.cpu_count()))))
outs = p.map(SaveSplit(headers), range(100))

print 'Merging vocabs'

procedures = set()
diagnoses = set()
labs = set()
prescriptions = set()

for (procs, diags, lab, prescs) in outs:
    procedures.update(procs)
    diagnoses.update(diags)
    labs.update(lab)
    prescriptions.update(prescs)

procedures = list(procedures)
diagnoses = list(diagnoses)
labs = list(labs)
prescriptions = list(prescriptions)

print 'procedures:', len(procedures)
print 'diagnoses:', len(diagnoses)
print 'labs:', len(labs)
print 'prescriptions:', len(prescriptions)

with open(pjoin(Out_dir, 'vocab_aux.pk'), 'wb') as f:
    pickle.dump({'procedures': procedures, 'diagnoses': diagnoses,
                 'labs': labs, 'prescriptions': prescriptions}, f, -1)
