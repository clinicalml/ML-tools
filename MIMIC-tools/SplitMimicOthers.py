import os
from os.path import join as pjoin

MIMIC_dir = '/home/jernite/MIMIC3'
output_dir = pjoin(MIMIC_dir, 'Parsed/MIMIC3_all')


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


for file_name in table_files + events_files:
    print file_name
    ct = 0
    f = open(pjoin(MIMIC_dir, file_name))
    print f.readline()
    patients = {}
    for line in f:
        batch_id = int(line.split(',')[1]) / 1000
        if batch_id >= 100:
            print line
            break
        patients[batch_id] = patients.get(batch_id, []) + [line]
        ct += 1
        if ct % 1000000 == 0:
            print ct
            for bid, lines in patients.items():
                of = open(pjoin(output_dir, '%02d/%s' % (bid, file_name)),'a')
                for l in lines:
                    print >>of, l
                of.close()
            patients = {}
    for bid, lines in patients.items():
        of = open(pjoin(output_dir, '%02d/%s' % (bid, file_name)),'a')
        for l in lines:
            print >>of, l
        of.close()
    f.close()


            

