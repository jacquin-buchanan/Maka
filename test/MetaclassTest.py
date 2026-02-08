class X(object):
    def __init__(self, x):
        self.x = x
        
class M(type):
    
    def __new__(cls, name, bases, attrs):
        
        xs = {}
        for name, value in attrs.items():
            if isinstance(value, X):
                xs[name] = value
                attrs[name] = value.x
                
        attrs['xs'] = xs
                
        return type.__new__(cls, name, bases, attrs)


class A(object, metaclass=M):
    pass
        
    
class B(A):
    b = X(1)
    
    
class C(B):
    c = X(2)
