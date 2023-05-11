from parse_python import parse_file, read_file_to_string
#from parse_cfg import parse_file_2cfg
from build import main
from cptm.utils import file_tqdm
import os
import traceback
import sys
import ast
import json

# ---------- parse pyhon2 files to cfg with parse_cfg.py ---------- #

data = r"C:/Users/ninas/OneDrive/Documents/UNI/Thesis/DATA/data2"
test = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/test_file.py"
full_out ='OUTPUT/full_data.json'
sample_out = 'OUTPUT/sample_data.json'

size = 50

def prep_path(path):
    x = '\\\\?\\' + path.replace('/','\\')
    return x

def test_path_prep():
    i = 0
    for root, _, files in os.walk(data):
        for file in files:
            if i < 10:
                prep_path(os.path.join(root, file)) 
                i =i+1
            else: return


def data_parser_cfg():
    i = 0
    with open(sample_out,'w') as out, open('OUTPUT/errorlog.txt', 'w') as errorlog :
        for root, _, files in os.walk(data):
            for file in files:
                if i > size:
                     print "finished :)"
                     return
                path = prep_path(os.path.join(root, file))
                try:
                    with open(path, 'r', )as f:
                        cfg_data = main(path,name=file)

                        print >>out, cfg_data
                        i = i+1
                        if (float(i)*100 /size) % 5 == 0:
                            print str(i*100 /size) + " percent"
                        
                except Exception as e:
                    i+=1
                    errorlog.write(path + " " + str(e) + "\n")
                    errorlog.write(traceback.format_exc() + "\n")
                    if  str(e) =="'Call' object has no attribute 'id'":
                        continue
    return

data_parser_cfg()
