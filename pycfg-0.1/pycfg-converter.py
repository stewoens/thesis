import pycfg.pycfg as pycfg

import json
import sys

# filepath = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/DATA/data3"
filepath = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/py2cfg/examples/else_02.py"

cfg,first,last = pycfg.get_cfg(filepath)
for i in sorted(cfg.keys()):
    print(i,'parents:', cfg[i]['parents'], 'children:', cfg[i]['children'])


 #incase dots is on ...whatever that means
# arcs = []
# cfg = pycfg.PyCFG()
# cfg.gen_cfg(pycfg.slurp(filepath).strip())
# g = pycfg.CFGNode.to_graph(arcs)
# g.draw(args.pythonfile + '.png', prog='dot')
# print(g.string(), file=sys.stderr)



