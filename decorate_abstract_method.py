from abc import ABC, abstractmethod

class Block(ABC):

    def __init__(self,id=1):
        self.id=id

    @abstractmethod # the method I want to decorate
    def run(self):
        pass

    def store_id(self,fun): # the decorator I want to apply
        def wrapper(fun):
            id=fun()
            self.id=id
            return id

        return wrapper

    def __init_subclass__(self):
        super().__init_subclass__()
        self.run = self.store_id(self.run)
        # do some other work
class Example(Block):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    def run(self):
        print("I am running")
        id=3
        return id

t=Example()
t.run()
print(t.id)
