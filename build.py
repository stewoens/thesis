"""
Control flow graph builder.
"""
import ast
from collections import defaultdict, deque
from mod import Link, TryBlock, FuncBlock, Block, CFG
import os
import aenum
from astprint import as_tree, as_code
from generate_seq import sequentialize_cfgs

test = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/example.py"

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
        op = type(node.ops[0])     #WHATISTHIS
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
    def __init__(self, try_block, after_block, has_final, ast, iter_state = None,):
        self.try_block = try_block
        self.after_block = after_block
        self.has_final = has_final
        self.iter_state = iter_state
        self.ast = ast

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

    
    def build(self, tree,path, entry_id = 0):
        """
        Build a CFG from an AST.

        Args:
            name: The name of the CFG being built.
            tree: The root of the AST from which the CFG must be built.
            async: Boolean indicating whether the CFG being built represents an
                   asynchronous function or not. When the CFG of a Python
                   program is being built, it is considered like a synchronous
                   'main' function.
            entry_id: Value for the id of the entry block of the CFG.

        Returns:
            The CFG produced from the AST.
        """
        self.cfg = CFG(path)
        self.current_id = entry_id
        self.current_block =self.new_block()
        self.cfg.entryblock = self.current_block
        self.traverse(tree,path)
        self.clean_cfg(self.cfg.entryblock, set())
        return self.cfg
    

    # ---------- Graph management methods ---------- #
    def new_block(self, statement = None):
        """
        Create a new block with a new id.

        Returns:
            A Block object with a new unique id.
        """

        self.current_id += 1
        block = Block(self.current_id)
        if statement is not None:
            block.add_statement(statement)
        return block

    def new_func_block(self):
        """
        Create a new function block with a new id.

        Returns:
            A FuncBlock object with a new unique id.
        """
        self.current_id += 1
        return FuncBlock(self.current_id)

    def new_try_block(self, statement=None):
        self.current_id += 1
        block = TryBlock(self.current_id)
        if statement is not None:
            block.add_statement(statement)
        return block

    def add_statement(self, block, node, is_module =False):
        """
        Add a statement to a block.

        Args:
            block: A Block object to which a statement must be added.
            statement: An AST node representing the statement that must be
                       added to the current block.
        """
        if is_module:
            block.statements.append(node)
            return

        s = as_code(node)

        if isinstance(node, ast.While):
            s = "while " + as_code(node.test) +":"
        elif isinstance(node, ast.Module):
            s = "Module"
        elif isinstance(node, ast.If):
            s = "if " + as_code(node.test) +":" 
        elif isinstance(node, ast.For):
            s = as_code(node).partition('\n')[0]
        elif isinstance(node, ast.FunctionDef):
            s = s.partition('\n')[0]
        elif isinstance(node, ast.ClassDef):
            s = s.partition('\n')[0]
        block.statements.append(s)

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

    def new_loopguard(self): #->Block
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

    # ---------- Building methods ---------- #

    def new_classCFG(self, node, asynchr = False):
        """
        Create a new sub-CFG for a class definition and add it to the
        class CFGs of the CFG being built.

        Args:
            node: The AST node containing the class definition.
            async: Boolean indicating whether the class for which the CFG is
                   being built is asynchronous or not.
        """
        self.current_id += 1
        # A new sub-CFG is created for the body of the class definition and
        # added to the class CFGs of the current CFG.
        class_body = ast.Module(body=node.body)
        class_builder = CFGBuilder(self.isShort, self._treebuf)
        self.cfg.classcfgs[node.name]= classcfg = class_builder.build(
            tree=class_body,path= node.name, entry_id= self.current_id
        )
        classcfg.lineno = node.lineno
#        classcfg.end_lineno = node.end_lineno  # type: ignore  #TODO something with ignore "'ClassDef' object has no attribute 'end_lineno'"
        self.current_id = class_builder.current_id + 1

    def new_functionCFG(self, node, asynchr):
        """
        Create a new sub-CFG for a function definition and add it to the
        function CFGs of the CFG being built.

        Args:
            node: The AST node containing the function definition.
            async: Boolean indicating whether the function for which the CFG is
                   being built is asynchronous or not.
        """
        self.current_id += 1
        # A new sub-CFG is created for the body of the function definition and
        # added to the function CFGs of the current CFG.
        func_body = ast.Module(body=node.body)
        func_builder = CFGBuilder(self.isShort, self._treebuf)
        cfg = self.cfg.functioncfgs[node.name]= func_builder.build(tree= func_body, path=node.name,entry_id= self.current_id)
        self.current_id = func_builder.current_id + 1
        cfg.lineno = node.lineno
        #cfg.end_lineno = node.end_lineno  # type: ignore   #TODO

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
        mylist.append(dict)
        modifiedlist = mylist
        for exit in block.exits:
            modifiedlist = self.show_blocks(exit.target, visited, mylist)
        return modifiedlist

    # ---------- AST Node visitor methods ---------- #

    def traverse(self, node, name= None):
         
        """
        Walk along the AST to generate CFG
        Args:
            tree (AST): the tree to be walked
        """
        
        #print node.__class__.__name__
        
    
        if isinstance(node, ast.Module):
            # if self.current_block.statements:
            #     mod_block = self.new_block()
            #     self.add_exit(self.current_block, mod_block)
            #     self.current_block = mod_block
            # else:
            #     self.add_statement(self.current_block, name)
            
            # next_block = self.new_block()
            # self.add_exit(self.current_block, next_block)
            # self.current_block = next_block
            self.add_statement(self.current_block, name, is_module = True)
            next_block = self.new_block()
            self.add_exit(self.current_block, next_block)
            self.current_block = next_block
            for child in node.body:
                self.traverse(child)

        elif isinstance(node, ast.ClassDef): #check
            self.add_statement(self.current_block, node)
            self.new_classCFG(node, asynchr=False)

        elif isinstance(node, ast.Expr): #check
            self.add_statement(self.current_block, node)
            self.generic_visit(node)

        elif isinstance(node, ast.Call):
            def visit_func(node):
                if isinstance(node, ast.Name):
                    return node.id
                elif isinstance(node, ast.Attribute):
                    # Recursion on series of calls to attributes.
                    func_name = visit_func(node.value)
                    if func_name is not None:
                        func_name = func_name + "." + node.attr
                        return func_name
                    else:
                        return node.attr
                        raise AttributeError(
                            "Func_name is None", type(node)
                        )

                elif isinstance(node, ast.Subscript):
                    if "id" in node.value._fields:
                        return node.value.id
                    elif "attr" in node.value._fields:
                        return visit_func(node.value)
                    elif isinstance(node.value, ast.Call):
                        return visit_func(node.value)
                    elif isinstance(node.value, ast.Subscript):
                        return visit_func(node.value)
                    else:
                        raise AttributeError(
                            "WTF is this thing, build it in??", type(node)
                        )
                elif isinstance(node, ast.Str):
                    e_id = node.s
                elif isinstance(node, ast.Call):
                    if "id" in node.func._fields:
                        return node.func.id
                    elif "attr" in node.func._fields:
                        return visit_func(node.func)
                    elif isinstance(node.func, ast.Call):
                        return visit_func(node.func)
                    
                    else:
                        raise AttributeError(
                            "WTF is this thing, build it in??", type(node)
                        )
                else:
                    print("WTF is this thing", type(node))
            func = node.func
            func_name = visit_func(func)
            if isinstance(node, ast.Call):
                print True
                func_block = self.new_func_block()
                self.add_statement(func_block, node)
                func_block.name = func_name

                if self._callbuf:
                    print "02"
                    # Func block is argument of last block in self._callbuf
                    self._callbuf[-1].args.append(func_block)
                else:
                    print "03"
                    # Not inside argument context.
                    self.current_block.func_calls.append(func_name)
                    self.current_block.func_blocks.append(func_block)

                self._callbuf.append(func_block)
                for arg in node.args:
                    self.traverse(arg)
                top = self._callbuf.pop()
                assert hash(top) == hash(func_block)
            else:
                self.current_block.func_calls.append(func_name)

        elif isinstance(node,ast.Assign): #check
            self.add_statement(self.current_block, node)
            self.generic_visit(node)
        
        elif isinstance(node, ast.AugAssign): #check
            self.add_statement(self.current_block, node)
            self.generic_visit(node)
        
        elif isinstance(node, ast.Print): #check
             self.add_statement(self.current_block, node)
        
        elif isinstance(node, ast.Raise):
            if self.current_block.statements:
                raise_block = self.new_block(node)
                self.current_block.add_exit(raise_block)
                self.current_block = raise_block
            else:
                self.current_block.add_statement(node)

            if not self.try_stack:
                # Raise statement outside of try block
                # If we don't know where control jumps, this is the last block
                self.current_block = self.new_block(node)
                return
            if isinstance(node.type, ast.Call):
                if isinstance(node.type.func, ast.Attribute):
                    if isinstance(node.type.func.value, ast.Attribute):
                        e_id = node.type.func.value.value.id
                    else:
                        e_id = node.type.func.value.id
                else: e_id = node.type.func.id
            elif isinstance(node.type, ast.Name):
                e_id = node.type.id
            elif isinstance(node.type, ast.Str):
                e_id = node.type.s
            elif isinstance(node.type, ast.Attribute):
                e_id = node.type.attr
            elif node.type is None:
                e_id = node.type
            else:
                raise ValueError("Unexpected object {0}".format(node.type))

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
                    
                    for child in tryobj.ast.finalbody:
                        if isinstance(child, ast.Raise):
                            top = self.try_stack.popleft()
                            break
                        self.traverse(child)
            self.current_block = self.new_block()

        elif isinstance(node,ast.Assert): #check
            self.add_statement(self.current_block, node)
            # New block for the case in which the assertion 'fails'.
            failblock = self.new_block()
            self.add_exit(self.current_block, failblock, invert(node.test))
            # If the assertion fails, the current flow ends, so the fail block is a
            # final block of the CFG.
            self.cfg.finalblocks.append(failblock)
            # If the assertion is True, continue the flow of the program.
            successblock = self.new_block()
            self.add_exit(self.current_block, successblock, node.test)
            self.current_block = successblock
            self.generic_visit(node)

        elif isinstance(node, ast.If): #check
            # If it already has something in it, we make a new block
            if self.current_block.statements:
                # Add the If statement at the beginning of the new block.
                cond_block = self.new_block()
                self.add_statement(cond_block, node)  #not node.test anymore
                self.add_exit(self.current_block, cond_block)
                self.current_block = cond_block
            else:
                # Add the If statement at the end of the current block.
                self.add_statement(self.current_block, node) #not node.test anymore
            if any(isinstance(node.test, T) for T in (ast.Compare, ast.Call)):
                self.traverse(node.test)
            # Create a new block for the body of the if. (storing the True case)
            if_block = self.new_block()

            self.add_exit(self.current_block, if_block, node.test)

            # Create a block for the code after the if-else.
            afterif_block = self.new_block()

            # New block for the body of the else if there is an else clause.
            if node.orelse:
    
                else_block = self.new_block() #TODO false case
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
        
        elif isinstance(node, ast.While): #check
            # TODO while/else

            loop_guard = self.new_loopguard()
            self.current_block = loop_guard
            self.add_statement(self.current_block,node)

            if isinstance(node.test, ast.Call):
                self.traverse(node.test)
            # New block for the case where the test in the while is True.
            while_block = self.new_block()

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

        elif isinstance(node,ast.For): #check
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

        elif isinstance(node, ast.Break): #check
            assert self.loop_stack
            after_block, _ = self.loop_stack[0]
            self.current_block.add_statement(node)
            self.current_block.add_exit(after_block)
            self.current_block = self.new_block()
        
        elif isinstance(node,ast.Continue): #check
            assert self.loop_stack
            
            _, loop_guard = self.loop_stack[0]
            self.add_statement(self.current_block,node)
            self.add_exit(self.current_block, loop_guard)
            self.current_block = self.new_block()
        
        elif isinstance(node, ast.Import): #check
            self.add_statement(self.current_block, node)

        elif isinstance(node, ast.ImportFrom): #check
             self.add_statement(self.current_block, node)
        
        
        elif isinstance(node,ast.FunctionDef): #check
            self.add_statement(self.current_block, node)
            self.new_functionCFG(node, asynchr=False)
        

        elif isinstance(node, ast.Return): #check
            if self.current_block.statements:
                return_block = self.new_block()
                self.current_block.add_exit(return_block)
                self.current_block = return_block

            self.add_statement(self.current_block, node)

            if self.try_stack:
                stackobj = self.try_stack[0]
                if stackobj.iter_state != TryEnum.FINAL and stackobj.has_final:
                    after_return = self.new_block()
                    self.current_block.add_exit(after_return)
                    after_return.add_exit(self.current_block)
                    self.current_block = after_return
                    for child in stackobj.node.finalbody:
                        self.traverse(child)

            self.cfg.finalblocks.append(self.current_block)
            # Continue in a new block but without any jump to it -> all code after
            # the return statement will not be included in the CFG.
            self.current_block = self.new_block()

        elif isinstance(node, ast.Yield): #check
            self.cfg.asynchr = True
            afteryield_block = self.new_block()
            self.add_exit(self.current_block, afteryield_block)
            self.current_block = afteryield_block


        elif  isinstance(node, ast.TryFinally):
            for c in node.body:
                if isinstance(c, ast.TryExcept):
                    self.visit_ExceptFinally(node)
                    return

            try_block = self.new_try_block(node)
            if self.current_block.is_empty():
                self.current_block = try_block
            else:
                self.current_block.add_exit(try_block)

            after_tryblock = self.new_block()
            self.current_block.add_exit(try_block)
            stackobj = TryStackObject(try_block, after_tryblock, bool(node.finalbody),node)
            self.try_stack.appendleft(stackobj)

            stackobj.iter_state = TryEnum.BODY
            self.current_block = try_block

            for child1 in node.body:
                self.traverse(child1)

            self.current_block.add_exit(after_tryblock)
            self.current_block = after_tryblock
            if node.finalbody:
                stackobj.iter_state = TryEnum.FINAL
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

        elif isinstance(node, ast.TryExcept):
            try_block = self.new_try_block(statement=node)

            if self.current_block.is_empty():
                self.current_block = try_block
            else:
                self.current_block.add_exit(try_block)
            

            after_tryblock = self.new_block()
            stackobj = TryStackObject(try_block, after_tryblock, False, node)
            self.try_stack.appendleft(stackobj)

            stackobj.iter_state = TryEnum.EXCEPT
            for child in node.handlers:
                self.current_block = self.new_block(statement=child)
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


            
            if node.orelse:
                stackobj.iter_state = TryEnum.ELSE
                else_block = self.new_block()
                self.current_block.add_exit(else_block)
                self.current_block = else_block
                for child2 in node.orelse:
                    self.traverse(child2)

            self.current_block.add_exit(after_tryblock)
            self.current_block = after_tryblock
                    
            del self.try_stack[0]

        elif isinstance(node, ast.ExceptHandler): #check
            assert self.try_stack
            ExceptBlock= self.new_block(node)
            #self.add_exit(self.current_block, ExceptBlock)
            for child in node.body:
                self.traverse(child)
            self.current_block.add_exit(self.try_stack[0].after_block)

        # ----------------GENERAL CASE--------------------#
        else:
            self.generic_visit(node)
            # #if the parent is a cfg node, a new node is createds     
            # if self.current_block.type() in stmnt_types:
            #     current_block = self.current_block
            #     new_block = self.new_block()
            #     self.add_exit(current_block, new_block)
            #     self.current_block =new_block
            # self.add_statement(self.current_block,  node)

    def generic_visit(self, node):
        """Called if no explicit visitor function exists for a node."""
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        self.traverse(item)
            elif isinstance(value, ast.AST):
                self.traverse(value)
    
    def visit_ExceptFinally(self, node):
        assert len(node.body) == 1
        assert isinstance(node.body[0], ast.TryExcept)
        try_block = self.new_try_block(statement=node.body[0])

        if self.current_block.is_empty():
            self.current_block = try_block
        else:
            self.current_block.add_exit(try_block)

        after_tryblock = self.new_block()
        stackobj = TryStackObject(try_block, after_tryblock, False, node)
        self.try_stack.appendleft(stackobj)

        stackobj.iter_state = TryEnum.EXCEPT
        for child in node.body[0].handlers:
            self.current_block = self.new_block(statement=child)
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
        for child1 in node.body[0].body:
            self.traverse(child1)
        
        if node.body[0].orelse:
            stackobj.iter_state = TryEnum.ELSE
            else_block = self.new_block()
            self.current_block.add_exit(else_block)
            self.current_block = else_block
            for child2 in node.orelse:
                self.traverse(child2)


        self.current_block.add_exit(after_tryblock)
        self.current_block = after_tryblock

        if node.finalbody:
            stackobj.iter_state = TryEnum.FINAL
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
        




   
def main(path, name):
    tree = ast.parse(read_file_to_string(path), path)
    cfgb = CFGBuilder()
    cfg = cfgb.build(tree, name)
    print cfg
    stmt_seq, e_seq = sequentialize_cfgs(cfg)

    return stmt_seq,e_seq


#main('\\\\?\\C:\\Users\\ninas\\OneDrive\\Documents\\UNI\\Productive-Bachelors\\DATA\\data2\\00\\wikihouse\\asset.py')
#main('\\\\?\\C:\\Users\\ninas\\OneDrive\\Documents\\UNI\\Productive-Bachelors\\example.py')