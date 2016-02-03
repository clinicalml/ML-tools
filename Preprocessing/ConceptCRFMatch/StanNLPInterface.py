# This is a wrapper function for the Stanford NLP suite (which is written
# in Java). You can get it at http://nlp.stanford.edu/software/corenlp.shtml.
# StanNLPdir must point to the downloaded jars.
# (Download teh version on the site, do not clone the GitHub repository).

import glob
import subprocess
import os
import xml.etree.ElementTree as et

from os.path import join as pjoin

num_threads_stan = 10

StanNLPdir = '/home/jernite/Tools/StanCoreNLP'

# ElementTree parses xml into a cumbersome tree structure, which we
# transform into nested dictionaries.
def treetodict(tree):
    res = {}
    for ch in tree.getchildren():
        if ch.tag not in res:
            res[ch.tag] = []
        if len(ch.getchildren()) == 0:
            res[ch.tag] = ch.text
        else:
            res[ch.tag] += [treetodict(ch)]
    return res


# This function calls the Stanford NLP tools on all the files in
# batch and returns a list of (filename, sentences).
# batch is a list of file locations to be parsed, nb is the number of the
# current batch
def stanford_parse(batch, nb, tempdir):
    devnull = open(os.devnull, 'wb')
    output_dir = pjoin(tempdir, 'output_xml_' + str(nb))
    subprocess.check_call('mkdir ' + output_dir, shell=True,
                          stdout=devnull, stderr=devnull)
    file_list = pjoin(output_dir, 'file_list_' + str(nb) + '.txt')
    for file_name in batch:
        subprocess.check_call('echo ' + file_name + ' >> ' + file_list,
                              shell=True, stdout=devnull, stderr=devnull)
    # Step 1: apply the StanfordNLP to the files listed in file_list
    jars = ':'.join(glob.glob(pjoin(StanNLPdir, '*.jar')))
    cmd = 'java -cp ' + jars \
        + ' -Xmx2g edu.stanford.nlp.pipeline.StanfordCoreNLP' \
        + ' -threads ' + str(num_threads_stan) \
        + ' -annotators tokenize,ssplit,pos,lemma' \
        + ' -filelist ' + file_list \
        + ' --outputDirectory ' + output_dir
    subprocess.check_call(cmd, shell=True, stdout=devnull, stderr=devnull)
    # Step 2: read the xml-formatted output into a list of dictionaries
    sent_list = []
    for text_file in glob.glob(pjoin(output_dir, '*.xml')):
        filename = text_file.split('/')[-1].split('.')[0]
        f = open(text_file)
        stanout = f.read()
        f.close()
        standict = treetodict(et.fromstring(stanout))
        try:
            stanlist = map(lambda x: x['tokens'][0]['token'],
                           standict['document'][0]['sentences'][0]['sentence'])
            sent_list += [(filename, stanlist[:])]
        except:
            print "failed " + text_file
    subprocess.check_call('rm -rf ' + output_dir, shell=True,
                          stdout=devnull, stderr=devnull)
    devnull.close()
    return sent_list
