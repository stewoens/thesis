from py2cfg.builder import CFGBuilder
from tqdm import tqdm
import json

"""
use py2cfg directly on py50k
"""

data = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/DATA/PY150/python50k_eval.json"
output = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/OUTPUT/cfg_data.json"
count = 0
with open(data, "r") as f, open(output, "w") as o:
    line = f.readline()
    dp = json.loads(line.strip())
    bui = CFGBuilder()
    cfg, mylist = bui.build(tree=dp,name="test_json")
    print(mylist)
    json_object= json.dumps(mylist, indent=4)
    
    o.write(json_object)
    count +=1