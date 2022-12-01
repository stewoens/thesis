import ast

absolute_path = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/py2cfg/examples/classy.py"

tree = ast.parse(read_file_to_string(absolute_path), absolute_path)
