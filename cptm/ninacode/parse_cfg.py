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
    
    def add_stuffs(n, kids, stmnts):
        if (len(kids) != 0):
            n['children'] = kids
        if (len(stmnts) != 0):
            n['statements'] = stmnts
        return n
        
    def new_node():
        return False
        """
        returns true if line needs new node. 
        false if it can be added to previous node
        """

    def traverse(node):
        pos = len(json_cfg)
        json_node = {}
        
        if pos == 0:
            json_cfg.append(json_node)
        if not new_node() and pos >0:
            if 'statements' in json_cfg[-1].keys():
                json_cfg[-1]["statements"].append(ast.dump(node))
            else:  
                json_cfg[-1]["statements"] =[ast.dump(node)] 
            return pos
        
        print "blub" + str(json_cfg[-1])
            
        children = []
        # access the last created node and add statements to it
        # json_cfg[-1:]['statements'].append
        # json_node['statements'] = type(node).__name__
        
        #nodes where child handling is not necessary 
        #should do some kind of testing 
        
        # if isinstance(node, ast.ImportFrom):
        #     statements.append(ast.dump(node))
        #     add_stuffs(json_node, children,statements)
        #     return pos
        # elif isinstance(node, ast.Import):
        #     statements.append(ast.dump(node))
        #     add_stuffs(json_node, children,statements)
        #     return pos
        # else: print type(node).__name__

        
        
        for child in ast.iter_child_nodes(node):
            children.append(traverse(child))
            print "traversing: " + str(traverse(child))
        print children
            
        json_node = add_stuffs(json_node, children, [])
    
        return pos
    
    traverse(tree)
    print json_cfg
    return json.dumps(json_cfg, separators=(',', ':'), ensure_ascii=False)

        