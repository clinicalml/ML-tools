class UMLSDescriptor:


   def __init__(self):
      self.mrconso_fields 	= ['CUI', 'LAT', 'TS', 'LUI', 'STT', 'SUI',
                              'ISPREF', 'AUI', 'SAUI', 'SCUI', 'SDUI',
                              'SAB', 'TTY', 'CODE', 'STR', 'SRL', 'SUPPRESS',
                              'CVF']
      self.mrconso_indices	= dict([(i, f)
                                   for i, f in enumerate(self.mrconso_fields)])
      self.mrdef_fields    = ['CUI', 'AUI', 'ATUI', 'SATUI', 'SAB', 'DEF',
                              'SUPPRESS', 'CVF']
      self.mrdef_indices   = dict([(i, f)
                                   for i, f in enumerate(self.mrdef_fields)])
      self.mrsty_fields    = ['CUI', 'TUI', 'STN', 'STY', 'ATUI', 'CVF']
      self.mrsty_indices   = dict([(i, f)
                                     for i, f in enumerate(self.mrsty_fields)])
      self.mrrel_fields    = ['CUI1', 'AUI1', 'STYPE1', 'REL',
                              'CUI2', 'AUI2', 'STYPE2', 'RELA',
                              'RUI', 'SRUI', 'SAB', 'SL', 'RG', 'DIR',
                              'SUPPRESS', 'CVF']
      self.mrrel_indices   = dict([(i, f)
                                   for i, f in enumerate(self.mrrel_fields)])


class ConceptIndex:


   def __init__(self, umls_desc):
      self.mappings  = {}
      self.umls_desc       = umls_desc


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
      self.add_link(source_code, source, cui)


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
      if is_concept_name:
         self.name   = name_str
      self.names  = list(set(self.names + [name_str]))
      self.codes[source] = self.codes.get(source, []) + [source_code]


   def add_mrdef_atom(self, line):
      indices  = self.umls_desc.mrdef_indices
      tab      = line.strip().split('|')
      source            = tab[indices['SAB']]
      definition        = tab[indices['DEF']]
      self.definitions  += (definition, source)


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
      self.relation_cuis   = list(set(self.relation_cuis.get(target, []) + \
                                      [relation]))
      self.relation_types  = list(set(self.relation_types.get(relation, []) + \
                                      [target]))

