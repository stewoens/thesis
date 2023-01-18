from DATA.parse_python import parse_file #check
from cptm.ninacode.parse_cfg import parse_file_2cfg
import os

data = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/DATA/data2"
test = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/DATA/data3/00/wikihouse/asset.py"
output ='OUTPUT/my_dataset'
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

 
def test_output():           
    with open(output,'w') as out, open(test, 'r')as f, open(test2, 'r')as g:
        print >>out, parse_file(test)
        print >>out, parse_file(test2)

def data_parser():
    i =0
    with open(output,'w') as out:
        for root, _, files in os.walk(data):
            for file in files:
                #test
                if i > 0:
                    continue
                path = prep_path(os.path.join(root, file))
                with open(path, 'r', )as f:
                    print >>out, parse_file_2cfg(path)
                    s = "done with file " + str(i)
                    print s
                    i = i+1
    print "finished :)"
    return

data_parser()




    