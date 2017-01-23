import cPickle as pickle

ndc_file = '/data/ml2/jernite/UMLS2016/RXNORM_RRF/RXNSAT.RRF'
rxcui_file = '/data/ml2/jernite/UMLS2016/MRCONSO_RXNORM.RRF'
icd9_file = '/data/ml2/jernite/UMLS2016/MRCONSO_ICD9.RRF'


def make_dics(ndc_file, rxcui_file, icd9_file):
    # NDC to CUI
    print ('making NDC to CUI dic')
    ndc_ro_rxcui = {}
    f = open(ndc_file)
    for line in f:
        tab = line.strip().split('|')
        if tab[8] == 'NDC':
            ndc_ro_rxcui[tab[10]] = ndc_ro_rxcui.get(tab[10], [])
            ndc_ro_rxcui[tab[10]] += [tab[0]]
            ndc_ro_rxcui[tab[10]] = list(set(ndc_ro_rxcui[tab[10]]))
    f.close()
    rxcui_to_cui = {}
    f = open(ndc_file)
    for line in f:
        tab = line.strip().split('|')
        if tab[8] == 'UMLSCUI':
            rxcui_to_cui[tab[0]] = ndc_ro_rxcui.get(tab[0], [])
            rxcui_to_cui[tab[0]] += [tab[10]]
            rxcui_to_cui[tab[0]] = list(set(rxcui_to_cui[tab[0]]))
    f.close()
    f = open(rxcui_file)
    for line in f:
        tab = line.strip().split('|')
        if tab[11] == 'RXNORM':
            rxcui_to_cui[tab[9]] = rxcui_to_cui.get(tab[9], [])
            rxcui_to_cui[tab[9]] += [tab[0]]
            rxcui_to_cui[tab[9]] = list(set(rxcui_to_cui[tab[9]]))

    f.close()
    ndc_to_cui = {}
    for ndc, rxcuis in ndc_ro_rxcui.items():
        ndc_to_cui[ndc] = list(set([cui for rxcui in rxcuis
                                    for cui in rxcui_to_cui.get(rxcui, [])]))
    ndc_to_cui = dict([(ndc, cuis[0])
                       for ndc, cuis in ndc_to_cui.items() if len(cuis) == 1])
    ndc_to_cui['0'] = 'UNK'
    # ICD9 to CUI
    print ('making ICD9 to CUI dic')
    icd9_to_cui = {}
    f = open(icd9_file)
    for line in f:
        tab = line.strip().split('|')
        if 'ICD9' in tab[11]:
            icd9_to_cui[tab[13]] = icd9_to_cui.get(tab[13], [])
            icd9_to_cui[tab[13]] += [tab[0]]
            icd9_to_cui[tab[13]] = list(set(icd9_to_cui[tab[13]]))
    f.close()
    return (ndc_to_cui, icd9_to_cui)


def map_to_cui(icd9, icd9_to_cui):
    if icd9 in icd9_to_cui:
        return icd9_to_cui[icd9]
    else:
        p1 = icd9[:-2] + '.' + icd9[-2:]
        p2 = icd9[:-1] + '.' + icd9[-1:]
        if p1 in icd9_to_cui and p2 in icd9_to_cui:
            # print 'AMBIGUOUS'
            return icd9_to_cui[p1]
        elif p1 in icd9_to_cui:
            return icd9_to_cui[p1]
        elif p2 in icd9_to_cui:
            return icd9_to_cui[p2]
        else:
            print 'MISSING'
            return []


def admission_summary(admission, ndc_to_cui, icd9_to_cui):
    res = {}
    res['PRESCRIPTIONS'] = [ndc_to_cui.get(presc[2][1], 'MISSED')
                            for presc in admission['PRESCRIPTIONS']]
    res['PROCEDURES'] = [cui for proc in admission['PROCEDURES']
                         for cui in map_to_cui(proc[0], icd9_to_cui)]
    res['DIAGNOSES'] = [cui for dx in admission['DIAGNOSES']
                        for cui in map_to_cui(dx[0], icd9_to_cui)]
    return res
