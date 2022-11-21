class Base:
    def __init__(self):
        print(self)


class Derived(Base):
    def __init__(self):
        super().__init__()
