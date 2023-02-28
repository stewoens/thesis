from DATA.parse_python import parse_file, read_file_to_string
#from parse_cfg import parse_file_2cfg
from build import main
import os
import traceback
import sys
import ast

# ---------- parse pyhon2 files to cfg with parse_cfg.py ---------- #

data = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/DATA/data2"
test = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/test_file.py"
output_cfg ='OUTPUT/my_dataset_cfg'
output_ast ='OUTPUT/my_dataset_ast'
cfg_data = 'OUTPUT/my_cfg'


def prep_path(path):
    x = '\\\\?\\' + path.replace('/','\\')
    return x

def test_path_prep():
    i = 0
    for root, _, files in os.walk(data):
        for file in files:
            if i < 10:
                print prep_path(os.path.join(root, file))
                i =i+1
            else: return

 
def test_output_cfg():           
    with open(output_cfg,'w') as out, open(path, 'r')as f:
        print >>out, parse_file_2cfg(test)
        print "finished :)"
        
def test_output_ast():           
    with open(output_ast,'w') as out, open(test, 'r')as f:
        print >>out, parse_file(test)
        print "finished :)"

def data_parser_cfg():
    i =0
    with open(output_cfg,'w') as out, open('OUTPUT/errorlog2.txt', 'w') as errorlog :
        for root, _, files in os.walk(data):
            for file in files:
                test
                # if i > 10000:
                #      print "finished :)"
                #      return
                path = prep_path(os.path.join(root, file))
                try:
                    with open(path, 'r', )as f:
                        print >>out, main(path)
                        # tree =ast.parse(read_file_to_string(path), path)
                        # print >>out, ast.dump(tree)
                        s = "done " + str(i)
                        print s
                        i = i+1
                except Exception as e:
                        errorlog.write(path + " " + str(e) + "\n")
                        # if not str(e) =="maximum recursion depth exceeded":
                        #     errorlog.write(traceback.format_exc() + "\n")
    print "finished :)"
    return

data_parser_cfg()




    