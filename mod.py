
import ast
from parse_cfg_test import parse_node
from typing import Any, Deque, Tuple, List, Optional, Iterator, Set, Dict

class Block(object):
    """
    CFG Block.

    A CFG Block contains statement, children and parents (and type?).
    """

    __slots__ = (
        "id",
        "statements",
        "func_calls",
        "predecessors",
        "exits",
        "func_blocks",
        "highlight",
        "outline",
    )

    def __init__(self, id):
        # Id of the block.
        self.id = id
        # Statements in the block.
        self.statements = []
        # Calls to functions inside the block (represents context switches to
        # some functions' CFGs).???
        self.func_calls = []
        # Links to predecessors in a control flow graph.
        self.predecessors=[]
        # Links to the next blocks in a control flow graph. 
        self.exits =[]
        # Function blocks within this block ???
        self.func_blocks= []
    
    def at(self):
        """
        Get the line number of the first statement of the block in the program.
        """
        if self.statements and self.statements[0].lineno >= 0:
            return self.statements[0].lineno
        return -1

    def end(self):
        """
        Get the line number of the last statement of the block in the program.
        """
        if self.statements and self.statements[-1].lineno >= 0:
            return self.statements[-1].lineno
        return -1

    def is_empty(self):
        """
        Check if the block is empty.

        Returns:
            A boolean indicating if the block is empty (True) or not (False).
        """
        return not self.statements
        

    def type(self, default = None):
        if default is None:
            default = ast.AST
        if self.statements:
            if isinstance(self.statements[0],basestring):
                return 'Module'
            return self.statements[0].__class__.__name__
        return default.__class__.__name__

    def add_statement(self, node):
        """
        Ive made node be dump(node)so far but maybe can be node as well?
        """
        parsed_node = parse_node(node)
        print parsed_node
        self.statements.append(parsed_node)
    
    #not sure how the exits work yet
    def add_exit(self, next, exitcase=None):
        link = Link(self, next, exitcase)
        self.exits.append(link)
        next.predecessors.append(link)
        
    def get_dict(block):   
        id = block.id
        text =block.statements
        type = block.type()
        children =[]
        for i in block.exits:
            children.append(i.target.id)
        
        
        #text removed for orga
        if type in ['If', 'True_Case','False_case','While','For'] or True:
            dict = {"id": id,"text":text, "children": children, "type": type}
        else:
            dict = {"id": id, "children": children, "type": type}
        return dict


class Link(object):
    """
    Link between blocks in a control flow graph.

    Represents a control flow jump between two blocks. Contains an exitcase in
    the form of an expression, representing the case in which the associated
    control jump is made.
    """

    __slots__ = (
        "source",
        "target",
        "exitcase",
        "highlight",
    )

    def __init__(
        self,
        source,
        target,
        exitcase= None,
    ):
        assert isinstance(target, Block), "Source of a link must be a block"
        assert isinstance(target, Block), "Target of a link must be a block"
        # Block from which the control flow jump was made.
        self.source = source
        # Target block of the control flow jump.
        self.target = target
        # 'Case' leading to a control flow jump through this link.
        self.exitcase = exitcase

    def __str__(self):
        return "link from {0} to {1}".format(self.source,self.target)

    def __repr__(self):
        # This isn't how repr is supposed to be used... We should be able to
        # deep copy this object by calling eval(repr(link))`.
        if self.exitcase is not None:
            return "{self}, with exitcase {ast.dump(self.exitcase)}"
        return str(self)

    def jumpfrom(self):
        """Return the line of source end"""
        return self.source.end()

    def jumpto(self):
        """Return the line of target start"""
        return self.target.at()

    #potentially add exitcase but needs astor, which i couldnt get
    
class FuncBlock(Block):
    __slots__ = ("args", "name")

    def __init__(self, *args, **kwargs):
        super(FuncBlock,self).__init__(*args, **kwargs)
        self.args = []
        self.name= None

class TryBlock(Block):
    __slots__ = ("except_blocks",)

    def __init__(self, id):
        super(TryBlock,self).__init__(id)
        self.except_blocks = {}

    def get_source(self):
        """
        Get a string containing the Python source code corresponding to the
        statements in the block.

        Returns:
            A string containing the source code of the statements.
        """
        if not self.statements[1:]:
            return "try:"
        src = ""
        for statement in self.statements[1:]:  # We just want try body
            if type(statement) in [ast.If, ast.For, ast.While]:
                src += astor.to_source(statement).split("\n")[0] + "\n"
            elif (
                type(statement) == ast.FunctionDef
                or type(statement) == ast.AsyncFunctionDef
            ):
                src += (astor.to_source(statement)).split("\n")[0] + "...\n"
            else:
                src += astor.to_source(statement)
        return src

class CFG(object):
    """
    Control flow graph (CFG).

    A control flow graph is composed of basic blocks and links between them
    representing control flow jumps. It has a unique entry block and several
    possible 'final' blocks (blocks with no exits representing the end of the
    CFG).
    """

    # Also serves as graph Key table
    # TODO Change value type to dict. Can be upacked into graph.node fn.

    def __init__(self, name):
        assert isinstance(name, str), "Name of a CFG must be a string"
        # Name of the function or module being represented.
        self.name = name
        # Entry block of the CFG.
        self.entryblock = None
        # Final blocks of the CFG.
        self.finalblocks = []
        # Sub-CFGs for functions defined inside the current CFG.
        self.functioncfgs = {}
        # Sub-CFGs
        self.classcfgs = {}

        self.lineno = 0
        self.end_lineno = 0
        self.qualname = ""
        
    def own_blocks(self):
        """
            Generator that yields all blocks in the current graph, excluding any
            subgraphs
        """
        visited = set()
        if self.entryblock is None:
            raise TypeError(
                "Expected self.entryblock to be not None but type is None"
            )
        to_visit = deque([self.entryblock])
        while to_visit:
            block = to_visit.popleft()
            visited.add(block)
            for exit_ in block.exits:
                if exit_.target in visited or exit_.target in to_visit:
                    continue
                to_visit.append(exit_.target)
            yield block




