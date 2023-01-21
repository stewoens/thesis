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

class Block(object):
    def __init__(self, id: int) -> None:
        # Id of the block.
        self.id = id
        # Statements in the block.
        self.statements: List[ast.AST] = []
        # Calls to functions inside the block (represents context switches to
        # some functions' CFGs).
        self.func_calls: List[str] = []
        # Links to predecessors in a control flow graph.
        self.parents: List[int] = []
        # Links to the next blocks in a control flow graph.
        self.children: List[int] = []

def setup_entry_block(node):
    entry = Block(0)
    entry.statements = node 

def read_file_to_string(filename):
    f = open(filename, 'rt')
    s = f.read()
    f.close()
    return s


def parse_file_2cfg(filename):
    global c, d
    tree = ast.parse(read_file_to_string(filename), filename)
    
    json_cfg = []
    current_pos =0

    def traverse(node):
        if current_pos == 0:
            setup_entry_block(node)
        pos = len(json_cfg)


        json_node = {}
        json_cfg.append(json_node)
        json_node['statements'] = type(node).__name__
        
        x = type(node).__name__
        if 'lineno' in node._attributes:
            y = getattr(node, 'lineno')
            print y
        else: print x
       
        
        children = []
        for child in ast.iter_child_nodes(node):
            children.append(traverse(child))
            
        if (len(children) != 0):
            #print "hello!!!"
            json_node['children'] = children
        return pos
       
    
    traverse(tree)
    return json.dumps(json_cfg, separators=(',', ':'), ensure_ascii=False)

# if __name__ == "__main__":
#     if len(sys.argv) != 2:
#         PrintUsage()
# print(parse_file(sys.argv[1]))
        