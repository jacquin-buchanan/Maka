from maka.data.Field import Float, Integer, String
from maka.data.Observation import Observation

from MakaTests import TestCase

    
class ObservationTests(TestCase):
    
    
    def testFieldInheritance(self):
        
        class A(Observation):
            a = String
            x = Integer
            
        class B(Observation):
            b = String
            
        class C(A, B):
            a = Integer
            c = String
            
        class D(C):
            x = Float
            d = Float
            
        self._assertFieldNames(D, 'a', 'b', 'c', 'd', 'x')
        self._assertFieldTypes(D, 'Integer', 'String', 'String', 'Float', 'Float')
            
            
    def _assertFieldNames(self, cls, *args):
        fieldNames = [f.name for f in cls.FIELDS]
        self.assertEqual(fieldNames, list(args))
        
        
    def _assertFieldTypes(self, cls, *args):
        typeNames = [f.__class__.__name__ for f in cls.FIELDS]
        self.assertEqual(typeNames, list(args))
        
        
    def testDefaultFieldOrder(self):
        
        class Obs(Observation):
            a = String
            c = String
            b = String
            
        fieldNames = [f.name for f in Obs.FIELDS]
        self.assertEqual(fieldNames, ['a', 'b', 'c'])
        
        
    def testDefaultFieldOrderWithInheritance(self):
        
        class A(Observation):
            x = String
            
        class B(Observation):
            b = String
            a = String
            
        class C(A, B):
            c = String
            b = Integer
            
        class D(C):
            y = String
            w = String
            
        self._assertFieldNames(A, 'x')
        self._assertFieldNames(B, 'a', 'b')
        self._assertFieldNames(C, 'a', 'b', 'c', 'x')
        self._assertFieldNames(D, 'a', 'b', 'c', 'w', 'x', 'y')
        
        # Make sure field `b` is an integer and not a string.
        fields = dict((f.name, f) for f in D.FIELDS)
        self.assertIsInstance(fields['b'], Integer)


    def testFieldInitByKwdArg(self):
        
        class Obs(Observation):
            x = String
            y = String
            
        obs = Obs(x='one', y='two')
        
        self.assertEqual(obs.x, 'one')
        self.assertEqual(obs.y, 'two')
        
        
    def testFieldAccessByName(self):
        
        class Obs(Observation):
            s = String
            
        self.assertIsInstance(Obs.s, String)
        self.assertIsInstance(getattr(Obs, 's'), String)
        
        
    def testEquality(self):
        
        class Obs(Observation):
            x = String
            y = Integer
            z = Float
            
        class Bobo(Obs):
            pass
        
        a = Obs(x='one', y=2, z=3)
        b = Obs(x='one', y=2, z=3)
        c = Bobo(x='one', y=2, z=3)
        
        self.assertTrue(a == a)
        self.assertFalse(a != a)
        
        self.assertTrue(a == b)
        self.assertFalse(a != b)
        
        # observations of different types are never equal
        self.assertTrue(a != c)
        self.assertFalse(a == c)
        
        b.x = 'zero'
        self.assertTrue(a != b)
        self.assertFalse(a == b)
            
        
    def testFieldAssignment(self):
        
        class P(Observation):
            x = String
            
        class Q(P):
            y = Integer
            
        a = Q(y=10)
        a.x = 'bobo'
        
        self.assertEqual(a.x, 'bobo')
        self.assertEqual(a.y, 10)
        
        
    def testReprAndStr(self):
        
        class P(Observation):
            y = Integer
            x = String
            
        cases = [
            (P(x='bobo'), "P(x='bobo', y=None)"),
            (P(y=10), "P(x=None, y=10)"),
            (P(x='bobo', y=10), "P(x='bobo', y=10)"),
            (P(x='bo"b\'o'), "P(x='bo\"b\\'o', y=None)")
        ]
        
        for a, expected in cases:
            self.assertEqual(repr(a), expected)
        
        
    def testCopy(self):
        
        class P(Observation):
            x = String
            y = Integer
            
        a = P(x='bobo', y=1)
        b = a.copy()
        
        self.assertIsInstance(b, P)
        self.assertEqual(b.x, 'bobo')
        self.assertEqual(b.y, 1)
        self.assertTrue(a is not b)
        self.assertEqual(a, b)
        
        
    def testCopyWithModification(self):
        
        class P(Observation):
            x = String
            y = Integer
            
        a = P(x='bobo', y=1)
        b = a.copy(y=2)
        
        self.assertIsInstance(b, P)
        self.assertEqual(b.x, 'bobo')
        self.assertEqual(b.y, 2)
        self.assertEqual(a.y, 1)
        
        
    # TODO: Elicit all error messages.
