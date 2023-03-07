import pydot
import ast
import json

menu = [{'text': [], 'type': 'Module', 'id': 0, 'children': [1]}, {'text': ["Import(names=[alias(name='ast', asname=None)])", "Print(dest=None, values=[Str(s='hello')], nl=True)"], 'type': 'Import', 'id': 1, 'children': []}]

def change_nodes(cfg):
    for d in cfg:
        for c in d.get("text"):
            if isinstance(c, ast.AST):
                cfg[d].get("text")[c] = ast.dump(c)




graph = pydot.Dot(graph_type='graph')

def draw(parent_name, child_name):
    edge = pydot.Edge(parent_name, child_name)
    graph.add_edge(edge)
    
def visit(cfg, parent=None):
    
    #print "cfg", cfg
    conv = eval(cfg)
    print conv
    for dic in conv:
        print dic
        for child in dic.get('children'):
            draw(dic.get('type'), conv[child].get('type'))

    return graph
    
        # for k,v in cfg.iteritems():# If using python3, use cfg.items() instead of cfg.iteritems()
        #     if isinstance(v, dict):
        #         # We start with the root cfg whose parent is None
        #         # we don't want to graph the None cfg
        #         if parent:
        #             draw(parent, k)
        #         visit(v, k)
        #     else:
        #         draw(parent, k)
        #         # drawing the label using a distinct name
        #         draw(k, k+'_'+v)

# graph = pydot.Dot(graph_type='graph')
# visit(menu)
# graph.write_png('example1_graph.png')