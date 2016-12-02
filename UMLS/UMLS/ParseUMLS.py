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
   parser.add_argument("-rxn", "--rxsat_file", default='/data/ml2/jernite/UMLS2016/RXNORM_RRF/RXNSAT.RRF',
                       help="location of the RRF files")
   parser.add_argument("-ml", "--max_lines", default=int(1e9), type=int,
                       help="cap the number of lines to read from a file")
   args = parser.parse_args()
   
   # start preparing
   umls_desc   = UMLSDescriptor()
   umls_index  = ConceptIndex(umls_desc)
   umls_dict   = {}
   
   # read MRCONSO.RRF
   print 'reading MRCONSO.RRF'
   mrconso_file   = open(pjoin(args.rrf_folder, 'MRCONSO.RRF'))
   lines_read     = 0
   for line in mrconso_file:
      cui            = line[:8]
      umls_dict[cui] = umls_dict.get(cui, Concept(cui, umls_desc))
      lines_read     += 1
      umls_dict[cui].add_mrconso_atom(line)
      umls_index.add_mrconso_atom(line)
      if lines_read % 200000 == 0:
         print 'MRCONSO.RRF', lines_read / 1000
         print str(umls_dict[cui])
      if lines_read > args.max_lines:
         break
   mrconso_file.close()
   
   # read RXNSAT.RRF
   if args.rxsat_file != '':
      print 'reading RXNSAT.RRF'
      umls_index.make_ndc_mapping(args.rxsat_file)
   # saving
   print 'saving the index'
   with open('umls_index.pk', 'wb') as pickle_file:
      pickle.dump(umls_index, pickle_file)
   
   # read MRDEF.RRF
   print 'reading MRDEF.RRF'
   mrdef_file  = open(pjoin(args.rrf_folder, 'MRDEF.RRF'))
   lines_read  = 0
   for line in mrdef_file:
      cui         = line[:8]
      lines_read  += 1
      if umls_dict.get(cui, False):
         umls_dict[cui].add_mrdef_atom(line)
         if lines_read % 200000 == 0:
            print 'MRDEF.RRF', lines_read / 1000
            print str(umls_dict[cui])
      if lines_read > args.max_lines:
         break
   mrdef_file.close()
   
   # read MRSTY.RRF
   print 'reading MRSTY.RRF'
   mrsty_file  = open(pjoin(args.rrf_folder, 'MRSTY.RRF'))
   lines_read  = 0
   for line in mrsty_file:
      cui         = line[:8]
      lines_read  += 1
      if umls_dict.get(cui, False):
         umls_dict[cui].add_mrsty_atom(line)
         if lines_read % 200000 == 0:
            print 'MRSTY.RRF', lines_read / 1000
            print str(umls_dict[cui])
      if lines_read > args.max_lines:
         break
   mrsty_file.close()
   
   # read MRREL.RRF
   print 'reading MRREL.RRF'
   mrrel_file  = open(pjoin(args.rrf_folder, 'MRREL.RRF'))
   lines_read  = 0
   for line in mrrel_file:
      cui         = line[:8]
      lines_read  += 1
      if umls_dict.get(cui, False):
         umls_dict[cui].add_mrrel_atom(line)
         if lines_read % 200000 == 0:
            print 'MRREL.RRF', lines_read / 1000
            print str(umls_dict[cui])
      if lines_read > args.max_lines:
         break
   mrrel_file.close()
   
   umls_shelve_dict  = shelve.open("umls_shelve_dict.shlf")
   umls_shelve_dict.update(umls_dict)
