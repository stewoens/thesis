from build import main
import os
import traceback
import json

# ---------- parse pyhon2 files to cfg with parse_cfg.py ---------- #


test = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/examples/class&func.py"

case = os.path.basename(test)

cfg_file = "OUTPUT/" + os.path.splitext(case)[0] + "_cfg.json"
edges_file = "OUTPUT/" + os.path.splitext(case)[0] + "_edges.json"


def prep_path(path):
    x = '\\\\?\\' + path.replace('/','\\')
    return x


def data_parser_cfg():
    path = prep_path(test)
    with open(cfg_file, 'w') as out_cfg, open('OUTPUT/errorlog.txt', 'w') as errorlog, open(path, 'r', )as f:
        try:
            cfgs = main(path)
            for cfg in cfgs:
                print >>out_cfg, json.dumps(cfg)
                
        except Exception as e:
            errorlog.write(str(e) + "\n")
            errorlog.write(traceback.format_exc())

data_parser_cfg()