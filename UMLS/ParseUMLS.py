import pickle
import shelve
import argparse

from os.path import join as pjoin

from UMLSUtils import *


if __name__ == "__main__":
   parser = argparse.ArgumentParser(description='This program \
                 reads the UMLS RRF files, and writes a shelf file.')
   parser.add_argument("-rrf", "--rrf_folder", default='Data/RRF',
                       help="location of the RRF files")
   args = parser.parse_args()
   # start preparing
   umls_desc 	= UMLSDescriptor()
   umls_index	= ConceptIndex(umls_desc)

