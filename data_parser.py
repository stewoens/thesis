from DATA.parse_python import parse_file #check
import os

data = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/DATA/data2"
test = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/DATA/data3/00/wikihouse/asset.py"
test2 = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/DATA/data3/00/wikihouse/auth.py"
output ='OUTPUT/my_dataset'

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
                # if i <140000:
                #     i = i+1
                #     print i
                #     continue
                path = prep_path(os.path.join(root, file))
                with open(path, 'r', )as f:
                    print >>out, parse_file(path)
                    s = "done with file " + str(i)
                    print s
                    i = i+1
    print "finished :\)"
    return

data_parser()




    