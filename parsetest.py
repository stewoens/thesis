from build import main
import os
import traceback
import json

# ---------- parse pyhon2 files to cfg with parse_cfg.py ---------- #


test = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/examples/return01.py"

case = os.path.basename(test)

output = "OUTPUT/" + os.path.splitext(case)[0] + ".json"

def prep_path(path):
    x = '\\\\?\\' + path.replace('/','\\')
    return x


def data_parser_cfg():
    path = prep_path(test)
    with open(output, 'w') as out, open('OUTPUT/errorlog.txt', 'w') as errorlog, open(path, 'r', )as f:
        try:
            cfg_data = main(path,name=case)
            print >>out, json.dumps(cfg_data)
                
        except Exception as e:
            errorlog.write(str(e) + "\n")
            errorlog.write(traceback.format_exc())

data_parser_cfg()