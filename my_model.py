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
    
class CFGBlock():
    """
    CFG Block.

    A CFG Block contains content, children and parents (and type?).
    """
    def __init__(self, id,typ):
        dict = {"id":id, "type":typ,"content":[],"children":[],"parents":[]}
        self.d= dict
        
    def __init__(self, id,type):
        # Id of the block.
        self.id = id
        # Statements in the block.
        self.content = []
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
        
    def at(self):
        """
        Get the line number of the first statement of the block in the program.
        """
        if self.content and self.content[0].lineno >= 0:
            return self.content[0].lineno
        return -1

    def end(self):
        """
        Get the line number of the last statement of the block in the program.
        """
        if self.content and self.content[-1].lineno >= 0:
            return self.content[-1].lineno
        return -1     

    def is_empty(self):
        """
        Check if the block is empty.

        Returns:
            A boolean indicating if the block is empty (True) or not (False).
        """
        return not self.content

    def add_content(self, node):
        """
        Ive made node be dump(node)so far but maybe can be node as well?
        """
        self.content.append(node)
    
    #not sure how the exits work yet
    def add_exit(self, next, exitcase=None):
        link = Link(self, next, exitcase)
        self.exits.append(link)
        next.predecessors.append(link)

