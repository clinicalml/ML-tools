import xml.etree.ElementTree as et
import pickle
from pprint import pprint

import sys
reload(sys)
sys.setdefaultencoding("ISO-8859-1")

def treetodict(tree):
	res={}
	for ch in tree.getchildren():
		if ch.tag not in res:
			res[ch.tag]=[]
		if len(ch.getchildren())==0:
			res[ch.tag]+=[ch.text]
		else:
			res[ch.tag]+=[treetodict(ch)]
	return res


def readXMLfile(file_name, max_visits=-1):
	f = open(file_name)
	visits = []
	failures = []
	ct = 0
	visit_str = ""
	index=""
	for l in f:
		if l == "":
			continue
		else:
			visit_str += l.replace('&', '+').encode('utf-8')
			if "</index>" in l:
				index=l.split('</index>')[0].split('>')[1]
			if "</visit>" in l:
				try:
					visits += [treetodict(et.fromstring(visit_str))]
				except Exception,e:
					print e
					failures += [(e, visit_str)]
				visit_str = ""
				index=""
				ct+=1
				if ct % 1000 == 0:
					print ct
				if ct == max_visits:
					break
	f.close()
	return visits, failures


[visits, failures]=readXMLfile('omr_batch_0.xml')

[visits, failures]=readXMLfile('deid_files.shuffle.nodate.xml')
