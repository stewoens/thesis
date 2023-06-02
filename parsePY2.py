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
test = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/examples"
full_out ='OUTPUT/full_data.json'
sample_out = 'OUTPUT/sample_data.json'
example_out = 'OUTPUT/example.json'
out_cfg = 'OUTPUT/cfgs.json'
out_edges = 'OUTPUT/edges.json'
size = 500

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
    with open(out_cfg,'w') as f_c, open(out_edges, 'w') as f_e, open('OUTPUT/errorlog.txt', 'w') as errorlog :
        for root, _, files in os.walk(data):
            for file in files:
                if i > size:
                     print "finished :)"
                     return
                path = prep_path(os.path.join(root, file))
                try:
                    with open(path, 'r', )as f:
                        cfgs, edges = main(path,name=file)
                        assert len(cfgs) == len(edges)

                        for cfg, e in zip(cfgs, edges):
                            if len(e)<3:
                                continue
                            print >>f_c, json.dumps(cfg)
                            print >>f_e, json.dumps(e)
                    i = i+1

                        
                except Exception as e:
                    i+=1
                    errorlog.write(path + " " + str(e) + "\n")
                    # if  str(e) =="'Call' object has no attribute 'id'":
                    #     continue
    return

data_parser_cfg()
