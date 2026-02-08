from maka.data.Field import Float
from maka.data.Observation import Observation

from FieldTests import FieldTests, fieldTestClass

    
_EPSILON = 1e-6


@fieldTestClass
class FloatFieldTests(FieldTests):
    
    
    fieldClass = Float
    validValue = 1.
    invalidValue = ''
    defaultTypeName = 'float'
    
    
    def testRangeProperty(self):
        
        cases = [
            (None, False, None, False, None),
            (None, False, 1, False, 'less than 1'),
            (None, False, 1, True, 'less than or equal to 1'),
            (1, False, None, False, 'greater than 1'),
            (1, True, None, False, 'greater than or equal to 1'),
            (1, False, 2, False, 'in (1, 2)'),
            (1, False, 2, True, 'in (1, 2]'),
            (1, True, 2, False, 'in [1, 2)'),
            (1, True, 2, True, 'in [1, 2]')
        ]
        
        for min, minInclusive, max, maxInclusive, range in cases:
            
            class Obs(Observation):
                f = Float(min=min, minInclusive=minInclusive, max=max, maxInclusive=maxInclusive)
                
            self.assertEqual(Obs.f.range, range)
            
            
    def testFloatFieldWithRestrictedRange(self):
        for min in [None, 1]:
            for minInclusive in [False, True]:
                for max in [None, 3]:
                    for maxInclusive in [False, True]:
                        self._testFloatFieldWithRestrictedRange(
                            min, minInclusive, max, maxInclusive)
                        
                        
    def _testFloatFieldWithRestrictedRange(self, min, minInclusive, max, maxInclusive):
        
        class Obs(Observation):
            v = Float(min=min, minInclusive=minInclusive, max=max, maxInclusive=maxInclusive)
            
        obs = Obs()
        
        badDefault = None
        
        if min is not None:
            
            if minInclusive:
                badStart = min - _EPSILON
                start = min
            else:
                badStart = min
                start = min + _EPSILON
                
            self._assertRaises(ValueError, setattr, obs, 'v', badStart)
            
            badDefault = min - 1
            
        else:
            start = -100
            
        obs.v = start
        self.assertEqual(obs.v, start)

        if max is not None:
            
            if maxInclusive:
                badEnd = max + _EPSILON
                end = max
            else:
                badEnd = max
                end = max - _EPSILON
                
            self._assertRaises(ValueError, setattr, obs, 'v', badEnd)
            
            badDefault = max + 1
            
        else:
            end = 100
            
        obs.v = end
        self.assertEqual(obs.v, end)
        
        n = 10
        for i in range(n):
            v = start + (end - start) / float(n - 1) * i
            obs.v = v
            self.assertEqual(obs.v, v)
            
        if badDefault is not None:
            self._assertRaises(
                ValueError, Float, **{'min': min, 'max': max, 'default': badDefault})
