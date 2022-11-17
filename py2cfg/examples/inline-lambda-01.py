def add(x, y):
    return x() + y()


add(lambda: 2, lambda: 2)
