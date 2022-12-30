import json
from tqdm import tqdm

from py2cfg.builder import CFGBuilder

input = 'DATA/PY150/python50k_eval.json'
output1 = 'OUTPUT/typelist.txt'
output2 = 'OUTPUT/if_trees.txt'
output3 = 'OUTPUT/example_ast.txt'


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
        
cfg_list = ["If"]

def interfere(ast):             #not tested, in terms of types etc.
    new_dp = []
    for i, node in enumerate(ast):
        if node["type"] in cfg_list:
            return True

    return False

with open(input, "r") as f, open(output2, "w") as fout:
        # for line in file_tqdm(f):
        #     dp = json.loads(line.strip())
        #     update_typelist(dp,file=fout,typelist=typelist)
        
        
        # sorted_lines = sorted(f.readlines(), key=lambda x: len(x))
        # line = sorted_lines[10000] 
        # dp =json.loads(line.strip())
        # write_ast(dp, fout)
        
        # for i, line in enumerate(f):
        #     if i in range(10000,20000):
        #         dp = json.loads(line.strip())
        #         bool = interfere(dp)
        #         if bool:
        #             fout.write(str(i) + "\n")
                    
        for i, line in enumerate(f):
            dp = json.loads(line.strip())
            if len(dp) < 100:
                if interfere(dp):
                    fout.write(str(i) + "\n")
                    
                    
                    
        
            
        
        
