import argparse
import shelve

import cPickle as pickle

from os.path import join as pjoin

from MimicPatient import *
from MimicEvent import *
from Utils import *


def read_patients_file(file_name, mimic_desc, max_lines=-1):
    patients     = {}
    for split_line in read_mimic_csv(file_name, max_lines=max_lines):
        try:
            patient = MimicPatient(mimic_desc, split_line)
            if patient.patient_id in patients:
                print "DUPLICATE OBSERVATIONS FOR PATIENT_ID:", patient.patient_id
            else:
                patients[patient.patient_id] = patient
        except:
            print "ERROR-------- Line", split_line
    return patients


def read_admissions_file(patients, file_name, mimic_desc, max_lines=-1):
    for split_line in read_mimic_csv(file_name, max_lines=max_lines):
        try:
            MimicAdmission(patients, mimic_desc, split_line)
        except:
            print "ERROR-------- Line", split_line


def read_events_file(patients, dir_name, mimic_desc, max_lines=-1):
    file_name = pjoin(dir_name, 'CPTEVENTS_DATA_TABLE.csv')
    for split_line in read_mimic_csv(file_name, max_lines=max_lines):
        try:
            CptEvent(patients, mimic_desc, split_line)
        except:
            print "ERROR-------- Line", split_line
    file_name = pjoin(dir_name, 'ICUSTAYEVENTS_DATA_TABLE.csv')
    for split_line in read_mimic_csv(file_name, max_lines=max_lines):
        try:
            IcuEvent(patients, mimic_desc, split_line)
        except:
            print "ERROR-------- Line", split_line
    file_name = pjoin(dir_name, 'LABEVENTS_DATA_TABLE.csv')
    for split_line in read_mimic_csv(file_name, max_lines=max_lines):
        try:
            LabEvent(patients, mimic_desc, split_line)
        except:
            print "ERROR-------- Line", split_line
    file_name = pjoin(dir_name, 'MICROBIOLOGYEVENTS_DATA_TABLE.csv')
    for split_line in read_mimic_csv(file_name, max_lines=max_lines):
        try:
            MicroEvent(patients, mimic_desc, split_line)
        except:
            print "ERROR-------- Line", split_line
    file_name = pjoin(dir_name, 'DRGCODES_DATA_TABLE.csv')
    for split_line in read_mimic_csv(file_name, max_lines=max_lines):
        try:
            DrugEvent(patients, mimic_desc, split_line)
        except:
            print "ERROR-------- Line", split_line
    file_name = pjoin(dir_name, 'PRESCRIPTIONS_DATA_TABLE.csv')
    for split_line in read_mimic_csv(file_name, max_lines=max_lines):
        try:
            PrescriptionEvent(patients, mimic_desc, split_line)
        except:
            print "ERROR-------- Line", split_line
    file_name = pjoin(dir_name, 'PROCEDURES_ICD_DATA_TABLE.csv')
    for split_line in read_mimic_csv(file_name, max_lines=max_lines):
        try:
            ProcedureEvent(patients, mimic_desc, split_line)
        except:
            print "ERROR-------- Line", split_line
    file_name = pjoin(dir_name, 'DIAGNOSES_ICD_DATA_TABLE.csv')
    for split_line in read_mimic_csv(file_name, max_lines=max_lines):
        DiagnosisEvent(patients, mimic_desc, split_line)
        try:
            DiagnosisEvent(patients, mimic_desc, split_line)
        except:
            print "ERROR-------- Line", split_line
    file_name = pjoin(dir_name, 'NOTEEVENTS_DATA_TABLE.csv')
    for split_line in read_mimic_csv(file_name, max_lines=max_lines):
        try:
            NoteEvent(patients, mimic_desc, split_line)
        except:
            print "ERROR-------- Line", split_line

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This program reads the \
                 MIMIC Patient files, and converts them to shelve format.')
    parser.add_argument("-dir", "--MIMIC3_directory", \
                        default='/data/ml2/MIMIC3/full',
                        help="Location of the MIMIC3 Patient files.")
    parser.add_argument("-o", "--output_file", \
                        default='patients.shlf',
                        help="Where to store the results")
    parser.add_argument("-ol", "--output_list", \
                        default='patients_list.pk',
                        help="Where to store the list of patient IDs")
    parser.add_argument("-ml", "--max_lines", \
                        default=-1, type=int,
                        help="maximum lines to be read in a file")
    args = parser.parse_args()
    #print args.MIMIC3_folder
    mimic_desc    = MimicDesc()
    patients_shelve  = shelve.open(args.output_file)
    file_name    = pjoin(args.MIMIC3_directory, 'PATIENTS_DATA_TABLE.csv')
    patients     = read_patients_file(file_name, mimic_desc) # , max_lines=args.max_lines)
    file_name    = pjoin(args.MIMIC3_directory, 'ADMISSIONS_DATA_TABLE.csv')
    read_admissions_file(patients, file_name, mimic_desc) # , max_lines=args.max_lines)
    dir_name     = pjoin(args.MIMIC3_directory)
    read_events_file(patients, dir_name, mimic_desc, max_lines=args.max_lines)
    patients_shelve.update(patients)
    with open(args.output_list, 'wb') as o_p:
        pickle.dump(patients.keys(), o_p)

