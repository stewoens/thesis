import ast
from astprint import as_tree, as_code

path = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/examples/example.py"

def read_file_to_string(filename):
    f = open(filename, 'rt')
    s = f.read()
    f.close()
    return s

with open(path, 'r', )as f:
    tree = ast.parse(read_file_to_string(path), path)
    print as_tree(tree, indent='  ')