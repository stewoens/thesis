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

    A CFG Block contains content, children and parents (and type?).
    """
    def __init__(self, id,typ):
        dict = {"id":id, "type":typ,"content":[],"children":[],"parents":[]}
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


    def new_block(self, typ, content=None):
            """
            Create a new block with a new id.

            Returns:
                A Block object with a new unique id.
            """
            self.current_id += 1
            block = CFGBlock(id =self.current_id, typ =typ)
            if content is not None:
                self.add_statement(block, content)

            self.cfg.append(block)
            
            return block
     
        
    def add_statement(self, block, content):
        """
        Add a content to a block.

        Args:
            block: A CFGBlock object to which a content must be added.
            content: An AST node representing the content that must be
                       added to the current block.
                       OR A STRING?
        """
        block.d["content"].append(content)
    
    
    def add_child(self, block, child):
        if child not in block.d["children"]:
            block.d["children"].append(child)
        

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
        #block =self.new_block(tree.__class__.__name__)
        
        
        self.traverse(tree)
        return self.cfg
        
        
    def traverse(self, node):
        """
        Walk along the AST to generate CFG

        Args:
            tree (AST): the tree to be walked
        return id of Block
        """
        
        # will a new block be generated after a specific content or before 
        #boolean wether can join old node or not (options are 1: add as content 
        #                                                  or 2: add to children (pos))
        pos = len(self.cfg)
        type= node.__class__.__name__
        
        # decide if the current node is Control Flow Relevant or not.
            
        if isinstance(node, ast.Module):
            current_block = self.new_block(type)
            pos+=1 
            for child in ast.iter_child_nodes(node):
                self.add_child(current_block, self.traverse(child))
            
        elif isinstance(node, ast.For):
            current_block = self.new_block(type)
            pos+=1 
            #dump target info
            self.add_statement(current_block,ast.dump(node.target))
            #dump iter info
            self.add_statement(self.cfg[-1],ast.dump(node.iter))
            print node.body
            for child in node.body:
                self.add_child(current_block, self.traverse(child))
                
        elif isinstance(node, ast.If):
            if self.current_block.statements:
                # Add the If statement at the beginning of the new block.
                cond_block = self.new_block()
                self.add_statement(cond_block, node)
                self.add_exit(self.current_block, cond_block)
                self.current_block = cond_block
            else:
                # Add the If statement at the end of the current block.
                self.add_statement(self.current_block, node)
            if any(isinstance(node.test, T) for T in (ast.Compare, ast.Call)):
                self.visit(node.test)
            # Create a new block for the body of the if. (storing the True case)
            if_block = self.new_block()

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
                    self.visit(child)
                self.add_exit(self.current_block, afterif_block)
            else:
                self.add_exit(self.current_block, afterif_block, invert(node.test))

            # Visit children to populate the if block.
            self.current_block = if_block
            for child in node.body:
                self.visit(child)
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
            if self.cfg[-1].d["type"] in stmnt_types:
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
    # for block in cfg:
    #     print block.d

main()
