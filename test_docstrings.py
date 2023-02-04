import ast, astunparse
data = '\\\\?\\C:\\Users\\ninas\\OneDrive\\Documents\\UNI\\Productive-Bachelors\\DATA\\data2\\00\\wikihouse\\asset.py'

with open(data) as f:
    lines = astunparse.unparse(ast.parse(f.read())).split('\n')
    for line in lines:
        if line.lstrip()[:1] not in ("'", '"'):
            print(line)
