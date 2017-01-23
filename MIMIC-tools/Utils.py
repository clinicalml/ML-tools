from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

def read_mimic_csv(file_name, max_lines=-1):
    split_line  = []
    cur_item    = ''
    try:
        f = open(file_name)
        print("Reading", file_name)
    except:
        print("ERROR-------- File", file_name, "not found.")
    read_lines = 0
    for line in f:
        if len(line.strip()) > 0:
            if max_lines > 0 and read_lines >= max_lines:
                break
            pre_split   = line.strip().split(',')
            for i, split_item in enumerate(pre_split):
                if cur_item != '':
                    if i > 0:
                        cur_item    += ','
                    cur_item    += split_item
                    if cur_item[-1] == '"':
                        split_line  += [cur_item.strip()[1:-1]]
                        cur_item    = ''
                elif split_item == '':
                    split_line  += [split_item]
                elif split_item[0] == '"':
                    if  split_item[-1] == '"' and len(split_item) > 1:
                        split_line  += [split_item[1:-1]]
                    else:
                        cur_item    = split_item
                else:
                    split_line  += [split_item]
            if cur_item == '':
                read_lines += 1
                yield split_line
                split_line  = []
            else:
                cur_item += ' \n '
    f.close()

