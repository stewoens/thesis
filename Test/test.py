import build
import pydot
import os
import traceback
from parse import parse_data, prep_path, unprep_path
from visualize import change_nodes, visit

examples = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/DATA/data2"


output = parse_data(examples)
j = 0
with open(output,'r') as out, open('OUTPUT/err_vis.txt', 'w') as errorlog:
    for line in out.read().splitlines():
        line.strip()
        conv = eval(line)
        rel_path = os.path.relpath( conv[0].get('text')[0], prep_path(examples))
        try:
            graph = visit(line)
            graph.write_png('OUTPUT/example{0}_graph.png'.format(j))
            print str(j) + " is " + rel_path
            j += 1
        except Exception as e:
            errorlog.write(rel_path + " " + str(e) + "\n")
            errorlog.write(traceback.format_exc() + "\n")
            j += 1
        


