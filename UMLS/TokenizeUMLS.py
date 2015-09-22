import os
import argparse
import ast
from nltk.tokenize import word_tokenize as split_tokens

input_file = 'UMLSlite.dat'
output_file = 'UMLStok.dat'


def tokenize_line(lst):
    res = lst[:]
    res[1] = ' '.join(split_tokens(res[1]))
    res[4] = [' '.join(split_tokens(st))
              for st in ast.literal_eval(res[4].strip())]


def main():
    f = open(input_file)
    preUMLS = [(line.strip() + ' ').split(' |||| ')[:-1] for line in f]
    f.close()
    print "Read UMLS"
    postUMLS = [preUMLS[0]] + [tokenize_line(ls) for ls in preUMLS[1:]
                               if len(ls) > 1]
    print "Processed UMLS"
    f = open(output_file, 'w')
    for line in postUMLS:
        for item in line:
            print >>f, item, '||||',
        print >>f, ''


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Some applications require \
      a tokenized version of UMLS strings. Let's do this once and for all")
    parser.add_argument("-i", "--umls_input",
                        help="text format input (UMLSlite.dat)")
    parser.add_argument("-o", "--umls_output",
                        help="text format output")
    args = parser.parse_args()
    if args.umls_input:
        input_file = args.umls_input
    if args.umls_output:
        output_file = args.umls_output
    input_file = os.path.abspath(input_file)
    output_file = os.path.abspath(output_file)
    print 'Starting'
    main()
