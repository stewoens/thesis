"""
Control flow graph builder.
"""
import ast
from itertools import count
from collections import defaultdict, deque
from typing import Dict, List, Optional, DefaultDict, Deque, Set, Union
from my_model import Link, TryBlock, CFGBlock, CFG
import os
import aenum

test = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/example.py"
stmnt_types = ['Module' , 'If', 'For', 'While', 'Break', 'Continue', 'ExceptHandler', 'With','ClassDef','FunctionDef']

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
    elif isinstance(node, ast.Name) and node.id in [True, False]:
        inverse_node = ast.Name(value=not node.id)
    else:
        inverse_node = ast.UnaryOp(op=ast.Not(), operand=node)

    return inverse_node


def merge_exitcases(exit1,exit2,):
    """
    Merge the exitcases of two Links.

    Args:
        exit1: The exitcase of a Link object.
        exit2: Another exitcase to merge with exit1.

    Returns:
        The merged exitcases.
    """
    if exit1:
        if exit2:
            return ast.BoolOp(ast.And(), values=[exit1, exit2])
        return exit1
    return exit2

def read_file_to_string(filename):
    f = open(filename, 'rt')
    s = f.read()
    f.close()
    return s


class TryEnum(aenum.IntEnum):
    BODY = aenum.auto()
    EXCEPT = aenum.auto()
    ELSE = aenum.auto()
    FINAL = aenum.auto()

class TryStackObject:
    def __init__(self, try_block, after_block, has_final, iter_state = None,):
        self.try_block = try_block
        self.after_block = after_block
        self.has_final = has_final
        self.iter_state = iter_state

    @property
    def node(self):
        return self.try_block.statements[0]  # type: ignore


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
    
    @property
    def try_stack(self):
        return self._treebuf["try_stack"]

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

            if not type == "Module":
                self.current_id += 1
            block = CFGBlock(id =self.current_id, type =type)
            if statement is not None:
                block.add_statement(statement)
            return block

            self.cfg.append(block)
            
            return block

    def new_try_block(self,type =None, statement=None):
        self.current_id += 1
        block = TryBlock(id =self.current_id,type=type)
        if statement is not None:
            block.add_statement(statement)
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

    def clean_cfg(self, block, visited):
        
        """
        Remove the useless (empty) blocks from a CFG.

        Args:
            block: The block from which to start traversing the CFG to clean
                   it.
            visited: A list of blocks that already have been visited by
                     clean_cfg (recursive function).
        """
        
        # Don't visit blocks twice.
        if block in visited:
            return
        visited.add(block)
        
        # Empty blocks are removed from the CFG.
        if block.is_empty():
            for pred in block.predecessors:
                for exit in block.exits:
                    self.add_exit(
                        pred.source,
                        exit.target,
                        merge_exitcases(pred.exitcase, exit.exitcase),
                    )
                    # Check if the exit hasn't yet been removed from
                    # the predecessors of the target block.
                    if exit in exit.target.predecessors:
                        exit.target.predecessors.remove(exit)
                # Check if the predecessor hasn't yet been removed from
                # the exits of the source block.
                if pred in pred.source.exits:
                    pred.source.exits.remove(pred)
        
            block.predecessors = []
            for exit in block.exits:
                self.clean_cfg(exit.target, visited)
            block.exits = []
        else:
            for exit in block.exits:
                self.clean_cfg(exit.target, visited)
    
    def show_blocks(self, block,visited, mylist):

        if block in visited:
            return mylist
        visited.add(block)
         
        dict = block.get_dict()
        #print dict
        mylist.append(dict)
        modifiedlist = mylist
        for exit in block.exits:
            modifiedlist = self.show_blocks(exit.target, visited, mylist)
        return modifiedlist
                
    def build(self, tree,path, entry_id = 0):
        """
        Build a CFG from an AST.

        Args:
            tree: The root of the AST from which the CFG must be built.
            entry_id: Value for the id of the entry block of the CFG.

        Returns:
            The CFG produced from the AST.
        """
        self.cfg = CFG(path)
        self.current_id = entry_id
        self.current_block =self.new_block(tree.__class__.__name__)
        self.cfg.entryblock = self.current_block
        
        self.traverse(tree,path)
        self.clean_cfg(self.cfg.entryblock, set())
        return self.cfg
        
        
    def traverse(self, node, path= None):
         
        """
        Walk along the AST to generate CFG
        Args:
            tree (AST): the tree to be walked
        """
        
        type= node.__class__.__name__
    
        if isinstance(node, ast.Module):
            if self.current_block.statements:
                mod_block = self.new_block(type)
                self.add_statement(mod_block, path)
                self.add_exit(self.current_block, mod_block)
                self.current_block = mod_block
            else:
                self.add_statement(self.current_block, path)
            
            for child in node.body:
                self.traverse(child) 
            
        elif isinstance(node,ast.For):
        
            # TODO for/else

            loop_guard = self.new_loopguard()
            self.current_block = loop_guard
            self.current_block.type =type
            self.add_statement(self.current_block, ast.dump(node.target))
            self.add_statement(self.current_block,ast.dump(node.iter))

            # New block for the body of the for-loop.
            for_block = self.new_block(type)
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

        elif isinstance(node, ast.While):
            loop_guard = self.new_loopguard()
            self.current_block = loop_guard
            self.current_block.type =type
            self.add_statement(self.current_block,ast.dump(node.test))

            # New block for the case where the test in the while is True.
            while_block = self.new_block(type)
            self.add_exit(self.current_block, while_block, node.test)

            # New block for the case where the test in the while is False.
            afterwhile_block = self.new_block()
            self.add_exit(self.current_block, afterwhile_block, invert(node.test))

            # Populate the while block.
            self.current_block = while_block
            self.loop_stack.appendleft((afterwhile_block, loop_guard))
            for child in node.body:
                self.traverse(child)
            top = self.loop_stack.popleft()
            assert top == (afterwhile_block, loop_guard)
            self.add_exit(self.current_block, loop_guard)

            # Continue building the CFG in the after-while block.
            self.current_block = afterwhile_block

        elif isinstance(node, ast.If):
            if self.current_block.statements:
                # Add the If statement at the beginning of the new block.
                cond_block = self.new_block(type)
                self.add_statement(cond_block,  ast.dump(node.test))
                self.add_exit(self.current_block, cond_block)
                self.current_block = cond_block
          
            else:
                # Add the If statement at the end of the current block.
                self.add_statement(self.current_block,  ast.dump(node.test))

            # Create a new block for the body of the if. (storing the True case)
            if_block = self.new_block('True_Case')

            self.add_exit(self.current_block, if_block, node.test)

            # Create a block for the code after the if-else.
            afterif_block = self.new_block()

            # New block for the body of the else if there is an else clause.
            if node.orelse:
                else_block = self.new_block("False_case")
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
        
        elif isinstance(node, ast.ClassDef):
            if self.current_block.statements:

                class_block = self.new_block(type)
                self.add_statement(class_block,node.name)
                self.add_exit(self.current_block, class_block)
                self.current_block = class_block
            elif self.current_block.type == "ClassDef":
                self.add_statement(self.current_block, node.name)

            for child in node.body:
                self.traverse(child) 

        elif isinstance(node,ast.FunctionDef):
            if self.current_block.statements:

                func_block = self.new_block(type)
                self.add_statement(func_block,node.name)
                self.add_exit(self.current_block, func_block)
                self.current_block = func_block
            elif self.current_block.type == 'FunctionDef':
                self.add_statement(self.current_block, node.name)

            for child in node.body:
                self.traverse(child) 

        elif isinstance(node, ast.Break):
            assert self.loop_stack
            after_block, _ = self.loop_stack[0]
            self.current_block.add_statement(ast.dump(node))
            self.current_block.add_exit(after_block)
            self.current_block = self.new_block()
        
        elif isinstance(node,ast.Continue):
            assert self.loop_stack
            _, loop_guard = self.loop_stack[0]
            self.add_statement(self.current_block,ast.dump(node))
            self.add_exit(self.current_block, loop_guard)
            self.current_block = self.new_block()
        
        elif isinstance(node, ast.Return):
            if self.current_block.statements:
                return_block = self.new_block(type)
                self.current_block.add_exit(return_block)
                self.current_block = return_block

            self.add_statement(self.current_block, ast.dump(node))

            if self.try_stack:
                stackobj = self.try_stack[0]
                if stackobj.iter_state != TryEnum.FINAL and stackobj.has_final:
                    after_return = self.new_block()
                    self.current_block.add_exit(after_return)
                    after_return.add_exit(self.current_block)
                    self.current_block = after_return
                    if isinstance(stackobj.node,str):
                        print "String1"
                        print stackobj.node
                    for child in stackobj.node.finalbody:
                        self.traverse(child)
            
            #not sure if i need finalblocks
            #self.cfg.finalblocks.append(self.current_block)
            # Continue in a new block but without any jump to it -> all code after
            # the return statement will not be included in the CFG.
            self.current_block = self.new_block()

        elif isinstance(node, ast.Raise):
            # if node.inst:
            #     print "node inst!!" + ast.dump(node.inst)
            # if node.tback:
            #     print "node tback!!" + ast.dump(node.tback)
            if self.current_block.statements:
                raise_block = self.new_block(type)
                self.current_block.add_exit(raise_block)
                self.current_block = raise_block
            else:
                self.current_block.add_statement(node)

            if not self.try_stack:
                # Raise statement outside of try block
                # If we don't know where control jumps, this is the last block
                self.current_block = self.new_block(type)
                return
            if isinstance(node.type, ast.Call):
                e_id = node.type.func.id
            elif isinstance(node.type, ast.Name):
                e_id = node.type.id
            else:
                raise ValueError("Unexpected object {1}".format(node.type))

            for tryobj in list(self.try_stack):

                def contains(item, state):
                    return (
                        item in tryobj.try_block.except_blocks
                        and tryobj.iter_state == state
                    )

                if contains(e_id, TryEnum.BODY):
                    # try:
                    #     raise StopIteration
                    # except StopIteration:
                    #     control_transfer_here = True
                    # except Exception:
                    #     control_transfer_here = False
                    self.current_block.add_exit(
                        tryobj.try_block.except_blocks[e_id]
                    )
                    break
                elif contains(None, TryEnum.BODY):
                    # try:
                    #     raise StopIteration
                    # except:
                    #     control_transfers_here = 1
                    self.current_block.add_exit(
                        tryobj.try_block.except_blocks[None]
                    )
                    break

                elif contains(e_id, TryEnum.EXCEPT) or contains(
                    None, TryEnum.EXCEPT
                ):
                    if tryobj.has_final:
                        _after_block = self.new_block()
                        self.current_block.add_exit(_after_block)
                        _after_block.add_exit(self.current_block)
                        self.current_block = _after_block

                        if isinstance(tryobj.node,str):
                            print "String2"
                        for child in tryobj.node.finalbody:
                            if isinstance(child, ast.Raise):
                                break
                            self.traverse(child)

                elif tryobj.iter_state == TryEnum.ELSE:
                    if tryobj.has_final:
                        _after_block = self.new_block()
                        self.current_block.add_exit(_after_block)
                        _after_block.add_exit(self.current_block)
                        self.current_block = _after_block
                        if isinstance(tryobj.node,str):
                            print "String3"
                        for child in tryobj.node.finalbody:
                            if isinstance(child, ast.Raise):
                                break
                            self.traverse(child)

                elif tryobj.iter_state != TryEnum.FINAL and tryobj.has_final:
                    # try: raise Exception
                    # finally: pass
                    _after_block = self.new_block()
                    self.current_block.add_exit(_after_block)
                    self.current_block = _after_block

                    if isinstance(tryobj.node,str):
                            print "String4"
                            print tryobj.node
                    for child in tryobj.node.finalbody:
                        if isinstance(child, ast.Raise):
                            top = self.try_stack.popleft()
                            break
                        self.traverse(child)
            self.current_block = self.new_block()

        elif isinstance(node,ast.Assert):
            self.add_statement(self.current_block, ast.dump(node))
            # New block for the case in which the assertion 'fails'.
            failblock = self.new_block('Fail_Block')
            self.add_exit(self.current_block, failblock, invert(node.test))
            # If the assertion fails, the current flow ends, so the fail block is a
            # final block of the CFG.
            # self.cfg.finalblocks.append(failblock)
            # If the assertion is True, continue the flow of the program.
            successblock = self.new_block()
            self.add_exit(self.current_block, successblock, node.test)
            self.current_block = successblock
         
        elif isinstance(node, ast.TryExcept) or isinstance(node, ast.TryFinally):
            f = isinstance(node, ast.TryFinally) #true if finally
            try_block = self.new_try_block(type=type)
            after_tryblock = self.new_block()
            self.current_block.add_exit(try_block)
            stackobj = TryStackObject(try_block, after_tryblock, f)
            self.try_stack.appendleft(stackobj)

            stackobj.iter_state = TryEnum.EXCEPT
            
            if not f:
                for child in node.handlers:
                    self.current_block = self.new_block()
                    # If we encounter a raise statement during body iteration,
                    # we can link the raise block to the appropriate exception block (if any).
                    try:
                        try_block.except_blocks[
                            None if child.type is None else child.type.id  # type: ignore
                        ] = self.current_block
                    except:
                        try_block.except_blocks[None] = self.current_block
                    self.traverse(child)

            stackobj.iter_state = TryEnum.BODY
            self.current_block = try_block
            for child1 in node.body:
                self.traverse(child1)

            if not f:
                stackobj.iter_state = TryEnum.ELSE
                else_block = self.new_block()
                self.current_block.add_exit(else_block)
                self.current_block = else_block
                for child2 in node.orelse:
                    self.traverse(child2)

            self.current_block.add_exit(after_tryblock)
            self.current_block = after_tryblock
            if f:
                stackobj.iter_state = TryEnum.FINAL

                if isinstance(node,str):
                            print "String5"
                for child3 in node.finalbody:
                    if isinstance(child3, ast.Raise):
                        top = self.try_stack.popleft()
                        self.traverse(child3)
                        self.try_stack.appendleft(top)
                        break
                    self.traverse(child3)
                else:
                    next_block = self.new_block()
                    self.current_block.add_exit(next_block)
                    self.current_block = next_block

            del self.try_stack[0]


        # ----------------GENERAL CASE--------------------#
        else:   
            #if the parent is a cfg node, a new node is created
            if self.current_block.type in stmnt_types:
                current_block = self.current_block
                new_block = self.new_block(type)
                self.add_exit(current_block, new_block)
                self.current_block =new_block
            
            
            self.add_statement(self.current_block,  ast.dump(node))
            if self.current_block.type == None:
                self.current_block.type = type
        
   
def main(path):
    tree = ast.parse(read_file_to_string(path), path)
    cfgb = CFGBuilder()
    cfg = cfgb.build(tree ,path)
    
    return cfgb.show_blocks(cfg.entryblock, set(),mylist=[])
    


#main('\\\\?\\C:\\Users\\ninas\\OneDrive\\Documents\\UNI\\Productive-Bachelors\\DATA\\data2\\00\\wikihouse\\asset.py')
main('\\\\?\\C:\\Users\\ninas\\OneDrive\\Documents\\UNI\\Productive-Bachelors\\example.py')