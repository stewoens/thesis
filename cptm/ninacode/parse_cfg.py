#!/usr/bin/python

import sys
import json as json
import ast


def PrintUsage():
    sys.stderr.write("""
Usage:
    parse_python.py <file>

""")
    exit(1)

def read_file_to_string(filename):
    f = open(filename, 'rt')
    s = f.read()
    f.close()
    return s

def parse_file_2cfg(filename):
    global c, d
    tree = ast.parse(read_file_to_string(filename), filename)
    
    
    
    json_cfg = []
    def gen_identifier(identifier, node_type = 'identifier'):
        pos = len(json_tree)
        json_node = {}
        json_tree.append(json_node)
        json_node['type'] = node_type
        json_node['value'] = identifier
        return pos
    
    def traverse_list(l, node_type = 'list'):
        pos = len(json_tree)
        json_node = {}
        json_tree.append(json_node)
        json_node['type'] = node_type
        children = []
        for item in l:
            children.append(traverse(item))
        if (len(children) != 0):
            json_node['children'] = children
        return pos
        
    def traverse(node):
        pos = len(json_cfg)
        json_node = {}
        json_cfg.append(json_node)
        json_node['type'] = type(node).__name__
        children = []
        for child in ast.iter_child_nodes(node):
            children.append(traverse(child))
            print child 
            return
        x = type(node).__name__
            
        if (len(children) != 0):
            print "hello!!!"
            json_node['children'] = children
        return pos
       
    
    traverse(tree)
    return json.dumps(json_cfg, separators=(',', ':'), ensure_ascii=False)

# if __name__ == "__main__":
#     if len(sys.argv) != 2:
#         PrintUsage()
# print(parse_file(sys.argv[1]))
        