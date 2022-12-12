import pycfg.pycfg as pycfg

import json
import sys

# filepath = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/DATA/data3"
filepath = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/py2cfg/examples/else_02.py"

with open('OUTPUT/example.json', 'w') as fjson:
    cfg,first,last = pycfg.get_cfg(filepath)
    for i in sorted(cfg.keys()):
        print(i,'parents:', cfg[i]['parents'], 'children:', cfg[i]['children'])
        # s = str(i)+ " " +'parents:'+ " " + str(cfg[i]['parents'])+ " " + 'children:'+ " " + str(cfg[i]['children']) + 'calls:'+ " " + str(cfg[i]['calls']) + "\n"
        # s = cfg
        fjson.write(str(i) + str(cfg[i]) + "\n")

