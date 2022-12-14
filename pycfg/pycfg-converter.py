import pycfg.pycfg as pycfg

import json
import sys
import os

# filepath = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/DATA/data3"
filepath = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/py2cfg/examples"

with open('OUTPUT/example.json', 'w') as fjson:
    for root, _, files in os.walk(filepath):
            for file in files:
                print(file)
                fpy = os.path.join(root, file)
                cfg,first,last = pycfg.get_cfg(fpy)
                for i in sorted(cfg.keys()):
                    # s = str(i)+ " " +'parents:'+ " " + str(cfg[i]['parents'])+ " " + 'children:'+ " " + str(cfg[i]['children']) + 'calls:'+ " " + str(cfg[i]['calls']) + "\n"
                    # print(s)
                    fjson.write(str(i) + str(cfg[i]) + "\n")

