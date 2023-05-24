from parse_python import parse_file, read_file_to_string
from build import main
from cptm.utils import file_tqdm
import os
import traceback
import sys
import ast
import json

# ---------- parse pyhon2 files to cfg with parse_cfg.py ---------- #


test01 = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/examples/return01.py"

case = os.path.basename(test01)

output = "OUTPUT/" + os.path.splitext(case)[0] + ".json"
print output

def prep_path(path):
    x = '\\\\?\\' + path.replace('/','\\')
    return x


def data_parser_cfg():
    path = prep_path(test01)
    with open(output, 'w') as out, open('OUTPUT/errorlog.txt', 'w') as errorlog, open(path, 'r', )as f:
        try:
            cfg_data = main(path,name=os.path.basename(test01))
            print >>out, json.dumps(cfg_data)
                
        except Exception as e:
            errorlog.write(path + " " + str(e) + "\n")
            errorlog.write(traceback.format_exc() + "\n")

    return

data_parser_cfg()