from tqdm import tqdm
import ast
import os

def file_tqdm(f):
    return tqdm(f, total=get_number_of_lines(f))

def create_filename(root, index):
    x  = root +"/file" + index
    print(x)

data = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/DATA/py150/python50k_eval.json"
root = r"OUTPUT/unparsed-data"
tmp = 0

def unparse_data():
    with open(data, "r") as f:
        output = create_filename(root,tmp)
        with open(output, "w") as fout:
            for line in file_tqdm(f):
                dp = json.loads(line.strip())
            
            
create_filename(root,tmp)