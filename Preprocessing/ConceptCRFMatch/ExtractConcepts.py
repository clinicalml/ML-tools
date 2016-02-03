import argparse

from pprint import pprint
from multiprocessing import Pool

from MakeCRFData import *
from ReadCRFOutput import *

data_dir = 'input_files'
UMLS_file = '../../Data/UMLStok.dat'
crf_mod_file = 'crf_model/model_overlaps.dat'

tmp_dir = 'tmp'

output_dir = 'output_files'

batch_size = 0
num_threads = 1
verbose = True


# process function for multiprocessing
def process_batch(x):
    devnull = open(os.devnull, 'wb')
    batch, nb = x
    print time.now(), '\t', "Launching Stanford NLP tools batch", nb
    sents = stanford_parse(batch, nb, tmp_dir)
    print time.now(), '\t', "Finished Stanford NLP tools batch", nb
    for note in sents:
        (note_id, sentences) = extract_features(note, trie, prefix_trie,
                                                acro_trie, spelling_trie)
        spans_file = pjoin(output_dir, 'spans_' + note_id + '.txt')
        features_file = pjoin(tmp_dir, 'text_' + note_id + 'pre_mrf.dat')
        crf_out_file = pjoin(tmp_dir, 'text_' + note_id + 'post_mrf.dat')
        write_crfpp_data(note_id, sentences, features_file, spans_file)
        cmd = 'crf_test -m ' + crf_mod_file + ' ' + features_file + ' -v2 > ' + crf_out_file
        subprocess.check_call(cmd, shell=True, stdout=devnull, stderr=devnull)
        sentences = treat_sentences(crf_out_file)
        pickle.dump(sentences, open(pjoin(output_dir, note_id + '.pk'), 'wb'))
        text_file = pjoin(output_dir, 'text_' + note_id + '.txt')
        f = open(text_file, 'w')
        for sent, mentions in sentences:
            print >>f, sentence
            for indices, men in mentions:
                for i in indices:
                    print >>f, i, 
                print >>f, '\t', men
            print >>f, ''
        f.close()
    devnull.close()
        


def main():
    global UMLS, lookup, trie, prefix_trie, suffix_trie, spelling_trie, acro_trie
    devnull = open(os.devnull, 'wb')
    # We first load UMLS
    UMLS, lookup, trie, prefix_trie, suffix_trie, \
        spelling_trie, acro_trie = read_umls(UMLS_file)
    # Then process files in the data directory (in parallel if batch_size > 0)
    file_list = glob.glob(pjoin(datadir, '*'))
    subprocess.call('mkdir ' + output_dir, shell=True, stdout=devnull)
    subprocess.call('mkdir ' + tmp_dir, shell=True, stdout=devnull)
    if batch_size == 0:
        batches = [file_list]
        process_batch((file_list, 1))
    else:
        n_batches = len(file_list) / batch_size
        batches = [file_list[i * batch_size: (i+1) * batch_size]
                   for i in range(n_batches)]
        batches += [file_list[n_batches * batch_size:]]
        p = Pool(num_threads)
        print p.map(process_batch,
                    [(batches[i], i + 1) for i in range(len(batches))])
    subprocess.check_call('rm -rf ' + tmp_dir, shell=True,
                          stdout=devnull, stderr=devnull)
    devnull.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This program takes all the \
     .text files in a DATA folder, does some some standard NLP and feature \
     extraction, and writes the output in a format which can be used by crf++ \
     for learning or prediction.')
    parser.add_argument("-nlp", "--corenlp",
                        help="location of the Stanford CoreNLP installation")
    parser.add_argument("-data", "--data",
                        help="location of folder containing the .txt files")
    parser.add_argument("-umls", "--umls",
                        help="UMLS text file (UMLSlite.dat)")
    parser.add_argument("-crf_mod", "--crf_model",
                        help="crf++ model file")
    parser.add_argument("-o", "--output",
                        help="output directory for the crfpp formatted files")
    parser.add_argument("-b", "--batch",
                        help="how many files to process at a time")
    parser.add_argument("-th", "--threads",
                        help="number of threads")
    parser.add_argument("-tmp", "--temp_dir",
                        help="specifies a temporary directory for StanCoreNLP")
    parser.add_argument("-v", "--verbose",
                        help="increase output verbosity", action="store_true")
    args = parser.parse_args()
    if args.corenlp:
        StanNLPdir = os.path.abspath(args.corenlp)
    if args.data:
        datadir = os.path.abspath(args.data)
    if args.umls:
        UMLS_file = os.path.abspath(args.umls)
    if args.umls:
        crf_mod_file = os.path.abspath(args.umls)
    if args.crf_model:
        output_dir = os.path.abspath(args.crf_model)
    if args.batch:
        batch_size = int(args.batch)
    if args.threads:
        num_threads = int(args.threads)
    if args.temp_dir:
        tmp_dir = os.path.abspath(args.temp_dir)
    if args.verbose:
        verbose = True
    main()
