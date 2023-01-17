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

def parse_file(filename):
    global c, d
    tree = ast.parse(read_file_to_string(filename), filename)
    
    
    
    json_tree = []
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
       
    
    traverse(tree)
    return json.dumps(json_tree, separators=(',', ':'), ensure_ascii=False)

# if __name__ == "__main__":
#     if len(sys.argv) != 2:
#         PrintUsage()
# print(parse_file(sys.argv[1]))
        