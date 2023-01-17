#from tqdm import tqdm
import ast
import json
import os

# def file_tqdm(f):
#     return tqdm(f, total=get_number_of_lines(f))

def create_filename(root, index):
    x  = root +"/file_" + str(index)
    return x 

data = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/DATA/py150/python50k_eval.json"
root = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/OUTPUT/unparsed-data"


def unparse_data():
    tmp = 0
    with open(data, "r") as f:
        for line in f:
            output = create_filename(root,tmp)
            tmp =tmp +1
            with open(output, "w") as fout:
                dp = json.loads(line.strip())
                print(dp.type())
                dp.unpa
                # fout.write(ast.unparse(dp))
                if tmp >= 1: return
    
            
            
unparse_data()