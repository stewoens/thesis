import json
from tqdm import tqdm
import ast

#from py2cfg.builder import CFGBuilder

input = 'DATA/PY150/python50k_eval.json'



def file_tqdm(f):
    return tqdm(f, total=get_number_of_lines(f))
    

def get_number_of_lines(fobj):
    nol = sum(1 for _ in fobj)
    fobj.seek(0)
    return nol

typelist =[]


def update_typelist(ast,file,typelist):
    for _, node in enumerate(ast):
        if "type" in node:
            if node["type"] not in typelist:
               typelist.append(node["type"])
               file.write(node["type"] + "\n")
    return typelist

def write_ast(ast,file):
        file.write(json.dumps(ast, indent=4))
        


def interfere(ast, type):             #not tested, in terms of types etc.
    new_dp = []
    for i, node in enumerate(ast):
        if node["type"]  == type:
            return True
    return False


def cfg_upgrade():
    for i, node in enumerate(ast):
        type = node["type"]
        match type:
            case "If":
                continue   
            case _: #default case
                # whatever
                continue
                
output1 = 'OUTPUT/typelist.txt'
output2 = 'OUTPUT/if_trees.txt'
output3 = 'OUTPUT/example_ast.txt'     
output4 = 'OUTPUT/small_if_example.txt'     

def main1():
    with open(input, "r") as f, open(output1, "w") as fout:
            for line in file_tqdm(f):
                dp = json.loads(line.strip())
                update_typelist(dp,file=fout,typelist=typelist)
                
def main2():
    with open(input, "r") as f, open(output2, "w") as fout:                        
            for i, line in enumerate(f):
                dp = json.loads(line.strip())
                if len(dp) < 40:
                    if interfere(dp, "If") and interfere(dp, "orelse"):
                        fout.write(str(i) + "\n")
                        
def main3():
    with open(input, "r") as f, open(output3, "w") as fout:           
            sorted_lines = sorted(f.readlines(), key=lambda x: len(x))
            line = sorted_lines[10000] 
            dp =json.loads(line.strip())
            write_ast(dp, fout)

def main4():
    with open(input, "r") as f, open(output4, "w") as fout:           
            for i, line in enumerate(f):
                if i == 463:
                    dp =json.loads(line.strip())
                    write_ast(dp, fout)
                    return
            
            
main4()