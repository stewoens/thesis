

error_types = ['Missing parentheses in call to \'print\'', 'ast.Subscript','ast.Call','ast.Constant', 'Unexpected object None', 'invalid syntax',
             'ast.Attribute', 'ast.BinOp','object has no attribute \'id\'', '+=','codec can', 'U+00BB',
             'inconsistent use of tabs','leading zeros in decimal integer literals', 'can\'t concat str to bytes',
             'Missing parentheses in call to', 'cannot assign to', 'maximum recursion']

with open('errorlog.txt') as oldfile, open('cleaned-errorlog.txt', 'w') as newfile:
    for line in oldfile:
        if not any(bad_word in line for bad_word in error_types):
            newfile.write(line)