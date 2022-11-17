import sys
import json

import pydot

def addChildren(i, data, graph):
    if "children" in data[i]:
        for c in data[i]["children"]:
            if 0 <= c < len(data):
                if "value" in data[c] and "type" in data[c]:
                    graph.add_node(pydot.Node(c, label=data[c]["type"] + "\n{}".format(data[c]["value"])))
                elif "value" in data[c] and not "type" in data[c]:
                    graph.add_node(pydot.Node(c, label="{}\n".format(c) + data[c]["value"]))
                elif "value" not in data[c] and "type" in data[c]:
                    graph.add_node(pydot.Node(c, label="{}\n".format(c) + data[c]["type"]))
                graph.add_edge(pydot.Edge(i, c, color="blue"))
                addChildren(c, data, graph)

def visualize(ast, outfile):
    graph = pydot.Dot(graph_type='graph')
    data = json.loads(ast)
    # Root node
    graph.add_node(pydot.Node(0, label=data[0]["type"]))
    # Create child nodes
    addChildren(0, data, graph)
    graph.write_png(outfile)