from parse_python import parse_file, read_file_to_string
import builder2 as b2
import os
import traceback
import sys
import ast

# ---------- parse pyhon2 files to cfg with parse_cfg.py ---------- #

data = r"C:/Users/ninas/OneDrive/Documents/UNI/Thesis/DATA/data2"
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

def parse2():
    i =0
    with open(output_cfg,'w') as out, open('OUTPUT/errorlog2.txt', 'w') as errorlog :
        for root, _, files in os.walk(data):
            for file in files:
                if i > 3:
                     print "finished :)"
                     return
                path = prep_path(os.path.join(root, file))


                cfgb =b2.CFGBuilder()
                cfgb.main(path,name= file)
                #print >>out, main(path, name =file)
                print "done " + str(i)
                i = i+1
                # except Exception as e:
                #     i+=1
                #     errorlog.write(path + " " + str(e) + "\n")
                #     if  str(e) =="'Call' object has no attribute 'id'":
                #         errorlog.write(traceback.format_exc() + "\n")
    print "finished :)"
    return

parse2()

