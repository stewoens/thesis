import pydot
import ast


def draw(parent_name, child_name):
    edge = pydot.Edge(parent_name, child_name)
    graph.add_edge(edge)
    
def visit(cfg, parent=None):
    for d in cfg:
        for c in d.get("children"):
            draw(d.get("type"), cfg[c].get("type"))
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

graph = pydot.Dot(graph_type='graph')
visit(menu)
graph.write_png('example1_graph.png')