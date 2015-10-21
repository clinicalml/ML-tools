import os
import glob
import re
from nltk.tokenize import word_tokenize as split_tokens
from os.path import join as pjoin
from time import gmtime, strftime

# List visit ids
os.system("grep \",\" NOTEEVENTS_DATA_TABLE.csv > id_lines.txt")
f = open('id_lines.txt')
desc = f.readlines()
f.close()
sub_ids = [int(x.split(',')[2]) for x in desc[1:]]

# First, split NOTEEVENTS_DATA_TABLE.csv into patient files
ct = 0
made_dir = []
note = []
num = '00000'

os.system("mkdir MIMIC3_text")
f = open("NOTEEVENTS_DATA_TABLE.csv")
for line in f:
    if '","' in line and not line[0] == '"':
        ct += 1
        if ct % 1000 == 0:
            print (100 * float(ct) / len(sub_ids))
        if len(note) > 0:
            if not num[:2] in made_dir:
                os.system("mkdir MIMIC3_text/%s" % (num[:2],))
                made_dir += [num[:2]]
            of = open("MIMIC3_text/%s/%s" % (num[:2], num), "a")
            print >>of, '<<<<<----->>>>>'       # optional. Note separator
            print >>of, '\n'.join(note)
            of.close()
            note = []
        num = '%05d' % (int(line.split(',')[2]),)
    note += [line.strip()]

f.close()
if len(note) > 0:
    if not num[:2] in made_dir:
        os.system("mkdir MIMIC3_text/%s" % (num[:2],))
        made_dir += [num[:2]]
    of = open("MIMIC3_text/%s/%s" % (num[:2], num[2:]), "a")
    print >>of, '<<<<<----->>>>>'
    print >>of, '\n'.join(note)
    f.close()


# Then, replace anonymization and tokenize
def treat_anon(match):
	anon = match.group()[3:-3]
	anon = re.sub('\d+', lambda x: 'num_' + str(len(x.group())), anon)
	anon = re.sub('[^0-9a-zA-Z]+', '_', anon)
	return 'ANON__' + '__'.join(anon.strip().split()) + '__ANON'


# normalize native anonymization
def treat_line(line):
	if '[**' in line:
		text = re.sub('\[\*\*.+?\*\*\]', treat_anon, line)
	else:
		text = line
	text = re.sub('\d{3,}', lambda x: 'num_' + str(len(x.group())), text)
	return ' '.join(split_tokens(text))

all_text = open('MIMIC_all_tokenized.txt', 'w')
os.system("mkdir MIMIC3_tokenized")
dirs = glob.glob(pjoin('MIMIC3_text', '*'))
for sub_dir in dirs:
	dir_num = sub_dir.split('/')[-1]
	print dir_num, strftime("%Y-%m-%d %H:%M:%S", gmtime())
	out_dir = pjoin('MIMIC3_tokenized', dir_num)
	os.system("mkdir %s" % (out_dir,))
	patient_files = glob.glob(pjoin(sub_dir, '*'))
	for file_name in patient_files:
		file_num = file_name.split('/')[-1]
		f = open(file_name)
		of = open(pjoin(out_dir, file_num), 'w')
		skip = 0
		paragraph = False
		for line in f:
			if line.strip() == '<<<<<----->>>>>':
				skip = 1
			elif skip == 1:
				tab = line.strip().split(',')
				note_type = tab[5][1:-1]
				date = tab[4]
				print >>of, 'NOTE_TYPE:\t', note_type, '\tDATE:\t', date
				skip = 0
			elif len(line.strip()) > 0:
				my_line = treat_line(line)
				print >>all_text, my_line,
				print >>of, my_line
				paragraph = True
			elif paragraph:
				print >>all_text, ''
				print >>of, ''
				paragraph = False
		of.close()
		f.close()

all_text.close()

##### Testing
f = open('MIMIC3_text/00/00009')
my_lines = f.readlines()
f.close()

for line in my_lines:
	if '[**' in line:
		print treat_line(line)


line = 'Social: Lots of family in to see, Sister [**Name (NI) 35**] [**Name (NI) 36**], RN, is identified as the next of [**Doctor First Name 37**], [**Last Name (un) **]-in-law [**First Name5 (NamePattern1) 38**] [**Last Name (NamePattern1) 39**] is a [**Hospital1 40**] Minister and prays with family in room, Girlfriend [**Name (NI) 41**] [**Name (NI) 42**] is Catholic and was visited by [**Hospital1 2**] priest on-call, family met with Social Work, updated by nursing'
