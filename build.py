"""
Control flow graph builder.
"""
import ast
test = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/example.py"

stmnt_types = ['Module' , 'If', 'For', 'While', 'Break', 'Continue', 'ExceptHandler', 'With']



def read_file_to_string(filename):
    f = open(filename, 'rt')
    s = f.read()
    f.close()
    return s


class CFGBlock():
    """
    CFG Block.

    A CFG Block contains statements, children and parents (and type?).
    """
    def __init__(self, id,typ):
        dict = {"id":id, "type":typ,"statements":[],"children":[],"parents":[]}
        self.d= dict
        

class CFGBuilder():
    """
    Control flow graph builder.

    A control flow graph builder is an ast.NodeVisitor that can walk through
    a program's AST and iteratively build the corresponding CFG.
    """

    def __init__(self):
        self.blocks =[]
        self.lineno = 0
        self.end_lineno = 0


    def new_block(self, typ, statement=None):
            """
            Create a new block with a new id.

            Returns:
                A Block object with a new unique id.
            """
            self.current_id += 1
            block = CFGBlock(id =self.current_id, typ =typ)
            if statement is not None:
                self.add_statement(block, statement)
            return block
     
        
    def add_statement(self, block, statement):
        """
        Add a statement to a block.

        Args:
            block: A CFGBlock object to which a statement must be added.
            statement: An AST node representing the statement that must be
                       added to the current block.
                       OR A STRING?
        """
        block.d["statements"].append(statement)
        

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
        self.current_block = self.new_block(tree.__class__.__name__)
        self.cfg.append( self.current_block)
        
        
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
        
        if type in stmnt_types:
            print "this works"
            
            for child in ast.iter_child_nodes(node):
                self.traverse(child)
        else:
            self.cfg[-1].d["statements"].append(ast.dump(node))
            
            
        
   
   
def main():
    tree = ast.parse(read_file_to_string(test), test)
    cfgb = CFGBuilder()
    cfg = cfgb.build(tree)
    for block in cfg:
        print block.d

main()
