import os
import glob
import re
from nltk.tokenize import word_tokenize as split_tokens
from os.path import join as pjoin
from time import gmtime, strftime

MIMIC_dir = '/home/jernite/MIMIC3'
output_dir = pjoin(MIMIC_dir, 'Parsed/MIMIC3_all')



# Replace anonymization and tokenize
def treat_anon(match):
	anon = match.group()[3:-3]
	# anon = re.sub('\d+', lambda x: 'num_' + str(len(x.group())), anon)
	anon = re.sub('[^0-9a-zA-Z]+', '_', anon)
	return 'ANON__' + '__'.join(anon.strip().split()) + '__ANON'


# normalize native anonymization
def treat_line(line):
	if '[**' in line:
		text = re.sub('\[\*\*.+?\*\*\]', treat_anon, line)
	else:
		text = line
	return text


def read_visit(lines):
	header = lines[0]
	bid = int(lines[0].split(',')[2]) / 1000
	if bid >= 100:
		pprint(lines[0])
		print lines[0].split(',')
		print lines[0].split(',')[2]
	text = [treat_line(line) for line in lines[1:]]
	res = ['\n']
	for line in text:
		if len(line) > 0:
			res += [line]
		elif len(res[-1].strip()) > 0:
				res += ['\n\n']
	return (bid, header, ' '.join(res))


for i in range(100):
    os.system('mkdir %s' % (pjoin(output_dir, '%02d' % (i,)),))

ct = 0
st = []
patients = {}
f = open(pjoin(MIMIC_dir, 'NOTEEVENTS_DATA_TABLE.csv'))
print f.readline()
for line in f:
	if line.strip() == '"':
		(bid, header, text) = read_visit(st)
		patients[bid] = patients.get(bid, []) + [(header, text)]
		st = []
		ct += 1
		if ct % 25000 == 0:
			print float(ct) / 2.5e4
			for bid, visits in patients.items():
				of = open(pjoin(output_dir, '%02d/NOTEEVENTS_DATA_TABLE.csv' % (bid,)),'a')
				for (header, text) in visits:
					print >>of, '<VISIT>'
					print >>of, header
					print >>of, text
					print >>of, '</VISIT>'
				of.close()
			patients = {}
	else:
		st += [line.strip()]
	

f.close()


########################
############ TODO: normalize numbers and tokenize
########################

# List visit ids
os.system("grep \",\" NOTEEVENTS_DATA_TABLE.csv > id_lines.txt")
f = open('id_lines.txt')
desc = f.readlines()
f.close()
sub_ids = [int(x.split(',')[2]) for x in desc[1:]]

# normalize native anonymization
def treat_line(line):
	if '[**' in line:
		text = re.sub('\[\*\*.+?\*\*\]', treat_anon, line)
	else:
		text = line
	text = re.sub('\d{3,}', lambda x: 'num_' + str(len(x.group())), text)
	return ' '.join(split_tokens(text))
