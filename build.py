"""
Control flow graph builder.
"""
import ast
from collections import defaultdict, deque
from typing import Dict, List, Optional, DefaultDict, Deque, Set, Union
from my_model import Link, CFGBlock

test = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/example.py"

stmnt_types = ['Module' , 'If', 'For', 'While', 'Break', 'Continue', 'ExceptHandler', 'With']

def invert(node): #: Union[Compare, ast.expr]
    """
    Invert the operation in an ast node object (get its negation).

    Args:
        node: An ast node object.

    Returns:
        An ast node object containing the inverse (negation) of the input node.
    """
    inverse = {
        ast.Eq: ast.NotEq,
        ast.NotEq: ast.Eq,
        ast.Lt: ast.GtE,
        ast.LtE: ast.Gt,
        ast.Gt: ast.LtE,
        ast.GtE: ast.Lt,
        ast.Is: ast.IsNot,
        ast.IsNot: ast.Is,
        ast.In: ast.NotIn,
        ast.NotIn: ast.In,
    }

    if isinstance(node, ast.Compare):
        op = type(node.ops[0])
        # inverse_Node is [ast.NameConstant, ast.UnaryOp, Compare]
        inverse_node = ast.Compare(left=node.left, ops=[inverse[op]()], comparators=node.comparators)
    elif isinstance(node, ast.NameConstant) and node.value in [True, False]:
        inverse_node = ast.NameConstant(value=not node.value)
    else:
        inverse_node = ast.UnaryOp(op=ast.Not(), operand=node)

    return inverse_node


def read_file_to_string(filename):
    f = open(filename, 'rt')
    s = f.read()
    f.close()
    return s


class CFGBuilder():
    """
    Control flow graph builder.

    A control flow graph builder is an ast.NodeVisitor that can walk through
    a program's AST and iteratively build the corresponding CFG.
    """

    def __init__(self, short = True, treebuf = None):
        self.isShort = short
        self._callbuf = []
        self._treebuf = defaultdict(deque) if treebuf is None else treebuf
    
    @property
    def loop_stack(self):
        return self._treebuf["loop_stack"]
        
    def new_loopguard(self):
        """
        Create a new block for a loop's guard if the current block is not
        empty. Links the current block to the new loop guard.

        Returns:
            The block to be used as new loop guard.
        """
        if self.current_block.is_empty() and len(self.current_block.exits) == 0:
            # If the current block is empty and has no exits, it is used as
            # entry block (condition test) for the loop.
            loopguard = self.current_block
        else:
            # Jump to a new block for the loop's guard if the current block
            # isn't empty or has exits.
            loopguard = self.new_block()
            self.add_exit(self.current_block, loopguard)

        return loopguard
    
    def new_block(self, type=None, statement=None):
            """
            Create a new block with a new id.

            Returns:
                A Block object with a new unique id.
            """
            self.current_id += 1
            block = CFGBlock(id =self.current_id, type =type)
            if statement is not None:
                self.add_statement(block, statement)

            self.cfg.append(block)
            
            return block
     
    def add_statement(self, block, statement):
        """
        Add a statement to a block.

        Args:
            block: A Block object to which a statement must be added.
            statement: An AST node representing the statement that must be
                       added to the current block.
        """
        block.statements.append(statement) 
        
    def add_exit(self,block,nextblock,exitcase = None): #Union[Compare, None, ast.BoolOp, ast.expr]
        """"
        Add a new exit to a block.

        Args:
            block: A block to which an exit must be added.
            nextblock: The block to which control jumps from the new exit.
            exitcase: An AST node representing the 'case' (or condition)
                      leading to the exit from the block in the program.
        """
        newlink = Link(block, nextblock, exitcase)  # type: ignore
        block.exits.append(newlink)
        nextblock.predecessors.append(newlink)   
        
# ---------- Building methods ---------- #

    def build(self, tree, entry_id = 0):
        """
        Build a CFG from an AST.

        Args:
            tree: The root of the AST from which the CFG must be built.
            entry_id: Value for the id of the entry block of the CFG.

        Returns:
            The CFG produced from the AST.
        """
        self.cfg = []
        self.current_id = entry_id
        self.current_block =self.new_block(tree.__class__.__name__)
        
        
        
        self.traverse(tree)
        return self.cfg
        
        
    def traverse(self, node):
        """
        Walk along the AST to generate CFG

        Args:
            tree (AST): the tree to be walked
        return id of Block
        """
        
        # will a new block be generated after a specific statement or before 
        #boolean wether can join old node or not (options are 1: add as statement 
        #                                                  or 2: add to children (pos))
        pos = len(self.cfg)
        type= node.__class__.__name__
        
        # decide if the current node is Control Flow Relevant or not.
            
        if isinstance(node, ast.Module):
            if self.current_block.statements:
                mod_block = self.new_block(type)
                self.add_statement(mod_block, node)
                self.add_exit(self.current_block, mod_block)
                self.current_block = mod_block
            else:
                self.add_statement(self.current_block, node)
            
            next_block = self.new_block()
            
            for child in node.body:
                self.traverse(child)
            self.add_exit(self.current_block, next_block)
                
            
            
        # elif isinstance(node, ast.For):
        elif isinstance(node,ast.For):
            # TODO for/else

            loop_guard = self.new_loopguard()
            self.current_block = loop_guard
            self.add_statement(self.current_block, node)

            if isinstance(node.iter, ast.Call):
                self.traverse(node.iter)
            # New block for the body of the for-loop.
            for_block = self.new_block()
            self.add_exit(self.current_block, for_block, node.iter)

            # Block of code after the for loop.
            afterfor_block = self.new_block()
            self.add_exit(self.current_block, afterfor_block)
            self.current_block = for_block

            # Push exit destinations for break/continue statements.
            # On break, control jumps to afterfor_block.
            # On continue, control jumps to loop_guard.
            self.loop_stack.appendleft((afterfor_block, loop_guard))

            # Populate the body of the for loop.
            for child in node.body:
                self.traverse(child)

            top = self.loop_stack.popleft()
            assert top == (afterfor_block, loop_guard)
            self.add_exit(self.current_block, loop_guard)

            # Continue building the CFG in the after-for block.
            self.current_block = afterfor_block
            #     current_block = self.new_block(type)
            #     pos+=1 
            #     #dump target info
            #     self.add_statement(current_block,ast.dump(node.target))
            #     #dump iter info
            #     self.add_statement(self.cfg[-1],ast.dump(node.iter))
            #     print node.body
            #     for child in node.body:
            #         self.add_exit(current_block, self.traverse(child))
                    
        elif isinstance(node, ast.If):
            if self.current_block.statements:
                # Add the If statement at the beginning of the new block.
                cond_block = self.new_block(type)
                self.add_statement(cond_block, node)
                self.add_exit(self.current_block, cond_block)
                self.current_block = cond_block
            else:
                # Add the If statement at the end of the current block.
                self.add_statement(self.current_block, node)
            if any(isinstance(node.test, T) for T in (ast.Compare, ast.Call)):
                self.traverse(node.test)
            # Create a new block for the body of the if. (storing the True case)
            if_block = self.new_block('True_Case')

            self.add_exit(self.current_block, if_block, node.test)

            # Create a block for the code after the if-else.
            afterif_block = self.new_block()

            # New block for the body of the else if there is an else clause.
            if node.orelse:
                else_block = self.new_block()
                self.add_exit(self.current_block, else_block, invert(node.test))
                self.current_block = else_block
                # Visit the children in the body of the else to populate the block.
                for child in node.orelse:
                    self.traverse(child)
                self.add_exit(self.current_block, afterif_block)
            else:
                self.add_exit(self.current_block, afterif_block, invert(node.test))

            # Visit children to populate the if block.
            self.current_block = if_block
            for child in node.body:
                self.traverse(child)
            self.add_exit(self.current_block, afterif_block)

            # Continue building the CFG in the after-if block.
            self.current_block = afterif_block

            # current_block = self.new_block(type)
            # pos+=1 
            # #dump test info
            # self.add_statement(current_block,ast.dump(node.test))
            
            # # have to create seperate children for each because otherwise true & false in same block
            # for child in node.body:
            #     self.add_child(current_block, self.traverse(child))
                
            # else_type= node.orelse[0].__class__.__name__
            # self.new_block(else_type)
            # pos+=1 
        
            # for child in node.orelse:
            #     self.add_child(current_block, self.traverse(child))
            
        # ----------------GENERAL CASE--------------------#
        else:    
            #if the parent is a cfg node, a new node is created
            if self.cfg[-1].type in stmnt_types:
                current_block =self.new_block(type)
                pos += 1
            else:current_block = self.cfg[-1]
                
            self.add_statement(self.cfg[-1], ast.dump(node))
            #general child traversing
            # for child in ast.iter_child_nodes(node):
            #     self.add_child(current_block, self.traverse(child))
            
        
            
        return pos
            
        
   
def main():
    tree = ast.parse(read_file_to_string(test), test)
    cfgb = CFGBuilder()
    cfg = cfgb.build(tree)
    for block in cfg:
        print block.get_dict()

main()
