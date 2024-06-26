
import ast
#from parse_python import traverse
from typing import Any, Deque, Tuple, List, Optional, Iterator, Set, Dict

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

        self.lineno = 0
        self.end_lineno= 0
        self.qualname = "" #dont know what this is for


    def _build_visual(self,format= "pdf",calls= True,interactive= False,build_own=False,):
        graph = gv.Digraph(name="cluster{0}{1}".format(self.subgraphs[self.name],self.name), format=format,
            graph_attr={
                "label": self.name,
                "rankdir": "TB",
                "ranksep": "0.02",
                "fontname": "DejaVu Sans Mono",
                "compound": "True",
                "pack": "False",
            },
            node_attr={"fontname": "DejaVu Sans Mono"},
            edge_attr={"fontname": "DejaVu Sans Mono"},
        )
        self.subgraphs[self.name] += 1
        if self.entryblock is None:
            raise TypeError(
                "Expected self.entryblock to be not None but type is None"
            )
        self._visit_blocks(
            graph,
            self.entryblock,
            visited=set(),
            calls=calls,
            format=format,
            interactive=interactive,
        )
        if build_own:
            return graph
        # Build the subgraphs for the function definitions in the CFG and add
        # them to the graph.
        for subcfg in self.classcfgs:
            subgraph = self.classcfgs[subcfg]._build_visual(
                format=format, calls=calls, interactive=interactive,
            )
            graph.subgraph(subgraph)

        for subcfg in self.functioncfgs:
            subgraph = self.functioncfgs[subcfg]._build_visual(
                format=format, calls=calls, interactive=interactive,
            )
            graph.subgraph(subgraph)
        return graph
   
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
        exitcase = None, #ast- Compare
    ):
        assert isinstance(target, CFGBlock), "Source of a link must be a block"
        assert isinstance(target, CFGBlock), "Target of a link must be a block"
        # CFGBlock from which the control flow jump was made.
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
    
class CFGBlock(object):
    """
    CFG Block.

    A CFG Block contains statement, children and parents (and type?).
    """
    # def __init__(self, id,typ):
    #     dict = {"id":id, "type":typ,"statement":[],"children":[],"parents":[]}
    #     self.d= dict
        
    def __init__(self, id,type):
        # Id of the block.
        self.id = id
        # Statements in the block.
        self.statements = []
        # type of the block
        self.type =type
        # Calls to functions inside the block (represents context switches to
        # some functions' CFGs).???
        self.func_calls = []
        # Links to predecessors in a control flow graph.
        self.predecessors= []
        # Links to the next blocks in a control flow graph. 
        self.exits = []
        # Function blocks within this block ???
        self.func_blocks = []
    
    # def get_source(self):
    #     """
    #     Get a string containing the Python source code corresponding to the
    #     statements in the block.

    #     Returns:
    #         A string containing the source code of the statements.
    #     """
    #     src = ""
    #     for statement in self.statements:
            
    #         if type(statement) in [ast.If, ast.For, ast.While]:
    #             src += codegen.to_source(statement).split("\n")[0] + "\n"
    #         elif (type(statement) == ast.FunctionDef or type(statement) == ast.FunctionDef):
    #             src += (codegen.to_source(statement)).split("\n")[0] + "...\n"
    #         else:
    #             src += codegen.to_source(statement)
    #     return src
    
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

    def add_statement(self, node):
        """
        Ive made node be dump(node)so far but maybe can be node as well?
        """
        self.statements.append(node)
    
    #not sure how the exits work yet
    def add_exit(self, next, exitcase=None):
        link = Link(self, next, exitcase)
        self.exits.append(link)
        next.predecessors.append(link)
        
    
     
    def get_dict(block):   
        id = block.id
        # try:
        #     text = block.get_source()
        #     print "not this"
        # except:
        text =block.statements
        text =[]
        for i in block.statements:
            if isinstance(i, ast.AST):
                text.append(ast.dump(i))
            else: 
                text.append(i)
        type = block.type
        children =[]
        for i in block.exits:
            children.append(i.target.id)
        
        
        #text removed for orga
        if type in ['If', 'True_Case','False_case','While','For'] or True:
            dict = {"id": id,"text":text, "children": children, "type": type}
        else:
            dict = {'id': id, 'children': children, 'type': type}
        return dict

class TryBlock(CFGBlock):
    __slots__ = ("except_blocks",)

    def __init__(self, id, type):
        super(TryBlock,self).__init__(id, type)
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

