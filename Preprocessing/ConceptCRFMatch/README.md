# Concept Extraction

Extracts medical concepts from text, and maps them to UMLS ids.

## Usage


```
usage: ExtractConcepts.py [-h] [-nlp CORENLP] [-data DATA] [-umls UMLS]
                          [-crf_mod CRF_MODEL] [-o OUTPUT] [-b BATCH]
                          [-th THREADS] [-tmp TEMP_DIR]

This program reads all the files in a DATA folder, as well as a CRF++ tagging
model, and identifies medical concepts.

optional arguments:
  -h, --help            show this help message and exit
  -nlp CORENLP, --corenlp CORENLP
                        location of the Stanford CoreNLP installation
  -data DATA, --data DATA
                        location of folder containing the text files
  -umls UMLS, --umls UMLS
                        UMLS text file (UMLSlite.dat / UMLStok.dat)
  -crf_mod CRF_MODEL, --crf_model CRF_MODEL
                        crf++ model file
  -o OUTPUT, --output OUTPUT
                        output directory
  -b BATCH, --batch BATCH
                        how many files to process at a time
  -th THREADS, --threads THREADS
                        number of threads
  -tmp TEMP_DIR, --temp_dir TEMP_DIR
                        specifies a temporary directory for StanCoreNLP and
                        CRF++
```

The first run takes about 12-15 minutes to parse UMLS, then this goes down to 3 minutes.

## Installation

You need:
- A working installation of [CRF++](https://taku910.github.io/crfpp/)
- A working installation of the [Stanford CoreNLP suite](http://nlp.stanford.edu/software/corenlp.shtml)
- A pre-processed UMLS file




