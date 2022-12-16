from parse_python import *
import os
import json

name = "cprm-test"

abspath = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/DATA/data3"
main = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/"

with open(main + f'OUTPUT/{name}.json', 'w') as fjson, open(main+'OUTPUT/errorlog.txt', 'w') as errorlog:
        for root, _, files in os.walk(abspath):
            for file in files:
                try:
                    f = os.path.join(root, file)
                    oi = parse_file(filename=f)
                    if oi is None:
                        print("ERROR: could not create entry: ",  file
                              )
                    else:
                        fjson.write(oi)
                except Exception as e:
                    errorlog.write(file + " " + str(e) + "\n")