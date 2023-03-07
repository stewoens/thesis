import build
import pydot
from parse import parse_data
from visualize import change_nodes, visit

examples = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/Test/examples"

output = parse_data(examples)
i = 0
with open(output,'r') as out:
    for line in out.read().splitlines():
        # print "line"
        # print line 
        line.strip()
        # print line
        
        graph = visit(line)
        graph.write_png('OUTPUT/example{0}_graph.png'.format(i))
        i += 1


