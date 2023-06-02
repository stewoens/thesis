from build import main
from cptm.utils import file_tqdm
import os
import traceback
import sys
import ast
import json

# ---------- parse pyhon2 files to cfg with parse_cfg.py ---------- #

data = "/storage/data/data/"
out_json ='/storage/cfg_data.json'
size = 50000

def data_parser_cfg():
    i = 0
    with open(out_json,'w') as out, open('OUTPUT/errorlog.txt', 'w') as errorlog :
        for root, _, files in os.walk(data):
            for file in files:
                if i > size:
                     print "finished :)"
                     return
                path = os.path.join(root, file)
                try:
                    cfgs = main(path)
                    for cfg in cfgs:
                        print >>out, json.dumps(cfg)
                    i = i+1

                        
                except Exception as e:
                    i+=1
                    errorlog.write(path + " " + str(e) + "\n")
                    # if  str(e) =="'Call' object has no attribute 'id'":
                    #     continue
    return

data_parser_cfg()
