from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from os.path import join as pjoin

MIMIC_dir = '/home/jernite/MIMIC3'
output_dir = pjoin(MIMIC_dir, 'Parsed/MIMIC3_split')


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



for i in range(100):
    os.system('mkdir %s' % (pjoin(output_dir, '%02d' % (i,)),))


def split_file(file_name):
    print(file_name)
    ct = 0
    f = open(pjoin(MIMIC_dir, file_name))
    print(f.readline())
    patients = {}
    for line in f:
        patient_id = line[:25].split(',')[1]
        patients[patient_id] = patients.get(patient_id, []) + [line]
        ct += 1
        if ct % 10000 == 0:
            print(ct / 1000, '\r', end=' ')
            sys.stdout.flush()
        if ct % 1000000 == 0:
            print(ct / 1000, len(patients))
            for pid, lines in list(patients.items()):
                bid = int(pid) / 1000
                if bid > 100:
                    pprint(lines)
                of = open(pjoin(output_dir, '%02d/%s' % (bid, file_name)),'a')
                for l in lines:
                    print(l, file=of)
                of.close()
            patients = {}
            print('next')
    for pid, lines in list(patients.items()):
        bid = int(pid) / 1000
        of = open(pjoin(output_dir, '%02d/%s' % (bid, file_name)),'a')
        for l in lines:
            print(l, file=of)
        of.close()
    f.close()


for file_name in ['CHARTEVENTS_DATA_TABLE.csv', 'IOEVENTS_DATA_TABLE.csv']:
    split_file(file_name)

    
for file_name in table_files + events_files:
    split_file(file_name)





