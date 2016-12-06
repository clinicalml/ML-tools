class UMLSDescriptor:


   def __init__(self):
      self.mrconso_fields   = ['CUI', 'LAT', 'TS', 'LUI', 'STT', 'SUI',
                              'ISPREF', 'AUI', 'SAUI', 'SCUI', 'SDUI',
                              'SAB', 'TTY', 'CODE', 'STR', 'SRL', 'SUPPRESS',
                              'CVF']
      self.mrconso_indices  = dict([(f, i)
                                   for i, f in enumerate(self.mrconso_fields)])
      self.mrdef_fields    = ['CUI', 'AUI', 'ATUI', 'SATUI', 'SAB', 'DEF',
                              'SUPPRESS', 'CVF']
      self.mrdef_indices   = dict([(f, i)
                                   for i, f in enumerate(self.mrdef_fields)])
      self.mrsty_fields    = ['CUI', 'TUI', 'STN', 'STY', 'ATUI', 'CVF']
      self.mrsty_indices   = dict([(f, i)
                                     for i, f in enumerate(self.mrsty_fields)])
      self.mrrel_fields    = ['CUI1', 'AUI1', 'STYPE1', 'REL',
                              'CUI2', 'AUI2', 'STYPE2', 'RELA',
                              'RUI', 'SRUI', 'SAB', 'SL', 'RG', 'DIR',
                              'SUPPRESS', 'CVF']
      self.mrrel_indices   = dict([(f, i)
                                   for i, f in enumerate(self.mrrel_fields)])
      self.rxnsat_fields   = ['RXCUI', 'LUI', 'SUI', 'RXATUI', 'STYPE', 'CODE',
                              'ATUI', 'SATUI', 'ATN', 'SAB', 'ATV',
                              'SUPPRESS', 'CVF']
      self.rxnsat_indices  = dict([(f, i)
                                   for i, f in enumerate(self.rxnsat_fields)])


class ConceptIndex:


   def __init__(self, umls_desc):
      self.mappings  = {}
      self.umls_desc = umls_desc


   def add_link(self, code, src, cui):
      self.mappings[src]         = self.mappings.get(src, {})
      self.mappings[src][code]   = self.mappings[src].get(code, [])
      self.mappings[src][code]   = list(set(self.mappings[src][code] + [cui]))


   def add_mrconso_atom(self, line):
      indices  = self.umls_desc.mrconso_indices
      tab      = line.strip().split('|')
      cui         = tab[indices['CUI']]
      source      = tab[indices['SAB']]
      source_code = tab[indices['CODE']]
      description = tab[indices['STR']]
      self.add_link(source_code, source, cui)
      self.add_link(description, 'STRING', cui)
      if source_code == 'RXNORM':
         rxcui = tab[indices['SCUI']]
         self.add_link(rxcui, 'RXCUI', cui)


   def find_code(self, code):
      res = []
      for name, mapping in self.mappings.items():
         if code in mapping:
            res += [(name, mapping[code])]
      return dict(res)


   def make_ndc_mapping(self, rxnsat_file):
      indices        = self.umls_desc.rxnsat_indices
      ndc_ro_rxcui   = {}
      f = open(rxnsat_file)
      for line in f:
         tab = line.strip().split('|')
         rxcui = tab[indices['RXCUI']]
         if (tab[indices['ATN']] == 'NDC'):
            ndc = tab[indices['ATV']]
            ndc_ro_rxcui[ndc] =  ndc_ro_rxcui.get(ndc, [])
            ndc_ro_rxcui[ndc] += [rxcui]
            ndc_ro_rxcui[ndc] =  list(set(ndc_ro_rxcui[ndc]))
         if (tab[indices['ATN']] == 'UMLSCUI'):
            cui   = tab[indices['ATV']]
            self.add_link(rxcui, 'RXCUI', cui)
      f.close()
      self.mappings['NDC'] = {}
      for ndc, rxcuis in ndc_ro_rxcui.items():
         self.mappings['NDC'][ndc] = list(set([cui for rxcui in rxcuis
                                               for cui in self.mappings['RXCUI'].get(rxcui, [])]))
      self.mappings['NDC']['0'] = 'UNK'


class Concept:


   def __init__(self, cui, umls_desc):
      self.cui             = cui
      self.umls_desc       = umls_desc
      self.name            = ''
      self.names           = []
      self.relation_cuis   = {}     # cui keys, descriptor values
      self.relation_types  = {}     # relation type keys, cui values
      self.codes           = {}     # other codes (ICD9, NDC, etc...)
      self.definitions     = []     # definitions from various sorces
      self.semantic_types  = []


   def add_mrconso_atom(self, line):
      indices  = self.umls_desc.mrconso_indices
      tab      = line.strip().split('|')
      is_concept_name   = (tab[indices['TTY']] == 'PN')
      source            = tab[indices['SAB']]
      source_code       = tab[indices['CODE']]
      name_str          = tab[indices['STR']]
      if is_concept_name or self.name == '':
         self.name   = name_str
      self.names           = list(set(self.names + [name_str]))
      self.codes[source]   = list(set(self.codes.get(source, []) + \
                                      [source_code]))


   def add_mrdef_atom(self, line):
      indices  = self.umls_desc.mrdef_indices
      tab      = line.strip().split('|')
      source            = tab[indices['SAB']]
      definition        = tab[indices['DEF']]
      self.definitions  += [(definition, source)]


   def add_mrsty_atom(self, line):
      indices  = self.umls_desc.mrsty_indices
      tab      = line.strip().split('|')
      sem_tree_path        = tab[indices['STN']]
      sem_type             = tab[indices['STY']]
      self.semantic_types  = list(set(self.semantic_types + \
                                      [(sem_type, sem_tree_path)]))


   def add_mrrel_atom(self, line):
      indices  = self.umls_desc.mrrel_indices
      tab      = line.strip().split('|')
      target   = tab[indices['CUI2']]
      general  = tab[indices['REL']]
      specific = tab[indices['RELA']]
      relation = (general, specific)
      self.relation_cuis[target]    = list(set(self.relation_cuis.get(target,
                                                                      []) + \
                                               [relation]))
      self.relation_types[relation] = list(set(self.relation_types.get(relation,
                                                                       []) + \
                                               [target]))


   def __str__(self):
      st =  'CUI:' + '\t' + self.cui + '\n'
      st += 'NAME:' + '\t' + self.name + '\n'
      st += 'TYPES:' + '\t' + str(self.semantic_types) + '\n'
      st += str(len(self.names)) + '\t NAMES \t'
      st += str(len(self.codes)) + '\t CODES \t'
      st += str(len(self.definitions)) + '\t DEFINITIONS \t'
      st += str(len(self.relation_cuis)) + '\t RELATIONS \n'
      return st
