ast = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
max_len = 9

# 1000
# 4320

def separate_dps(ast, max_len):

    asts = []
    i = max_len

    if len(ast) <= max_len:
        return [[ast]]
    
    asts.append([ast[:max_len]])
    
    while i < len(ast) - max_len:
        asts.append([ast[i : i + max_len]])
        i += max_len

    asts.append(ast[i:])

    return asts

print(separate_dps(ast, max_len))