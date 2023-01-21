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
    tree = ast.parse(read_file_to_string(filename), filename)
    
    json_cfg = []
    current_pos =0

    def traverse(node):
        pos = len(json_cfg)
        json_node = {}
        json_cfg.append(json_node)
        children = []
        # access the last created node and add statements to it
        json_cfg[-1:]['statements'].append
        json_node['statements'] = type(node).__name__
        
        if isinstance(node, ast.ImportFrom):
            json
            
        # last thought is node an ast.AST? if yes add to statement as there wont be any other arrows from it 
        
        
        # x = type(node).__name__
        # if 'lineno' in node._attributes:
        #     y = getattr(node, 'lineno')
        #     print y
        # else: print x
       
        
        children = []
        for child in ast.iter_child_nodes(node):
            children.append(traverse(child))
            
        if (len(children) != 0):
            #print "hello!!!"
            json_node['children'] = children
        return pos
       
    
    traverse(tree)
    return json.dumps(json_cfg, separators=(',', ':'), ensure_ascii=False)

        