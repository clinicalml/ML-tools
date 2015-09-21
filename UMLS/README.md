#UMLS

Processes the cumbersome MRCONSO.RRF, MRSTY.RRF, etc... into a leaner and
cleaner text format.

Provides tools to use this text version of UMLS.

ProcessUMLS.py reads the RRF files and writes a single text (or pickle)
file with the summarized information

TreeUMLS.py uses ProcessUMLS to read the file and builds a tree on concepts
consistent with the ontology
