from maka.data.Field import Integer
from maka.data.Observation import Observation

from FieldTests import FieldTests, fieldTestClass

    
@fieldTestClass
class IntegerFieldTests(FieldTests):
    
    
    fieldClass = Integer
    validValue = 1
    invalidValue = ''
    defaultTypeName = 'integer'
    
    
    def testRangeProperty(self):
        
        cases = [
            (None, None, None),
            (None, 1, 'less than or equal to 1'),
            (1, None, 'greater than or equal to 1'),
            (1, 2, 'in [1, 2]')
        ]
        
        for min, max, range in cases:
            
            class Obs(Observation):
                i = Integer(min=min, max=max)
                
            self.assertEqual(Obs.i.range, range)
            
            
    def testIntegerFieldWithRestrictedRange(self):
        for min in [None, 1]:
            for max in [None, 3]:
                self._testIntegerFieldWithRestrictedRange(min, max)
                        
                        
    def _testIntegerFieldWithRestrictedRange(self, min, max):
        
        class Obs(Observation):
            i = Integer(min=min, max=max)
            
        obs = Obs()
        
        badDefault = None
        
        if min is not None:
            first = min
            self._assertRaises(ValueError, setattr, obs, 'i', first - 1)
            badDefault = min - 1
        else:
            first = 0
            
        if max is not None:
            last = max
            self._assertRaises(ValueError, setattr, obs, 'i', last + 1)
            badDefault = max + 1
        else:
            last = 4
        
        for i in range(first, last + 1):
            obs.i = i
            self.assertEqual(obs.i, i)
            
        if badDefault is not None:
            self._assertRaises(
                ValueError, Integer, **{'min': min, 'max': max, 'default': badDefault})
