# This is a wrapper function for the Stanford NLP suite (which is written
# in Java). You can get it at http://nlp.stanford.edu/software/corenlp.shtml.
# StanNLPdir must point to the downloaded jars.
# (Download teh version on the site, do not clone the GitHub repository).

import xml.etree.ElementTree as et
from os.path import join as pjoin
import glob
import os

num_threads_stan = 10
remove_r = True		# TODO: fix

tmpdir = '/tmp'
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
def stanford_parse(batch, nb, tempdir=tmpdir):
    os.system('mkdir ' + tempdir)
    output_dir = pjoin(tempdir, 'output_xml_' + str(nb))
    os.system('mkdir ' + output_dir)
    file_list = pjoin(output_dir, 'file_list_' + str(nb) + '.txt')
    # If the file was written in Windows, we need to remove the \r in the
    # newlines
    if remove_r:
        new_batch = [pjoin(output_dir, text_file.split('/')[-1] + '.nor')
                     for text_file in batch]
        for text_file, new_file in zip(batch, new_batch):
            cmd = "tr -d '\r' < " + text_file + ' > ' + new_file
            os.system(cmd)
            cmd = "sed -i 's,/,\,,g' " + new_file
            os.system(cmd)
        for file_name in new_batch:
            os.system('echo ' + file_name + ' >> ' + file_list)
    else:
        for file_name in batch:
            os.system('echo ' + file_name + ' >> ' + file_list)
    # Step 1: apply the StanfordNLP to the files listed in file_list
    jars = ':'.join(glob.glob(pjoin(StanNLPdir, '*.jar')))
    cmd = 'java -cp ' + jars \
        + ' -Xmx2g edu.stanford.nlp.pipeline.StanfordCoreNLP' \
        + ' -threads ' + str(num_threads_stan) \
        + ' -annotators tokenize,ssplit,pos,lemma' \
        + ' -filelist ' + file_list \
        + ' --outputDirectory ' + output_dir
    print cmd
    os.system(cmd)
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
    os.system('rm -rf ' + output_dir)
    return sent_list
