from maka.data.Field import Decimal
from maka.data.Observation import Observation

from FieldTests import FieldTests, fieldTestClass

    
_EPSILON = 1e-6


@fieldTestClass
class DecimalFieldTests(FieldTests):
    
    
    fieldClass = Decimal
    validValue = '1'
    invalidValue = ''
    defaultTypeName = 'decimal'
    
    
    def testDecimalRe(self):
        
        from maka.data.Field import _DECIMAL_RE as r

        for case in ['0', '123', '0.', '0.123', '.123', '12.34']:
            self.assertIsNotNone(r.match(case))
            self.assertIsNotNone(r.match('-' + case))
            
        for case in ['.', '1e10', '123e']:
            self.assertIsNone(r.match(case))
            
            
    def testRangeProperty(self):
        
        cases = [
            (None, False, None, False, None),
            (None, False, '1', False, 'less than 1'),
            (None, False, '1', True, 'less than or equal to 1'),
            ('1', False, None, False, 'greater than 1'),
            ('1', True, None, False, 'greater than or equal to 1'),
            ('1', False, '2', False, 'in (1, 2)'),
            ('1', False, '2', True, 'in (1, 2]'),
            ('1', True, '2', False, 'in [1, 2)'),
            ('1', True, '2', True, 'in [1, 2]')
        ]
        
        for min, minInclusive, max, maxInclusive, range in cases:
            
            class Obs(Observation):
                d = Decimal(min=min, minInclusive=minInclusive, max=max, maxInclusive=maxInclusive)
                
            self.assertEqual(Obs.d.range, range)
            
            
    def testDecimalFieldWithRestrictedRange(self):
        for min in [None, '1']:
            for max in [None, '3']:
                for minInclusive in [False, True]:
                    for maxInclusive in [False, True]:
                        self._testDecimalFieldWithRestrictedRange(
                            min, max, minInclusive, maxInclusive)

    
    def _testDecimalFieldWithRestrictedRange(self, minStr, maxStr, minInclusive, maxInclusive):
         
        class Obs(Observation):
            v = Decimal(min=minStr, max=maxStr,
                        minInclusive=minInclusive, maxInclusive=maxInclusive)
             
        obs = Obs()
        
        min = None if minStr is None else float(minStr)
        max = None if maxStr is None else float(maxStr)
        
        badDefault = None
         
        if min is not None:
             
            if minInclusive:
                badStart = min - _EPSILON
                start = min
            else:
                badStart = min
                start = min + _EPSILON
                 
            self._assertRaises(ValueError, setattr, obs, 'v', str(badStart))
             
            badDefault = min - 1
             
        else:
            start = -100
             
        startStr = str(start)
        obs.v = startStr
        self.assertEqual(obs.v, startStr)
 
        if max is not None:
             
            if maxInclusive:
                badEnd = max + _EPSILON
                end = max
            else:
                badEnd = max
                end = max - _EPSILON
                 
            self._assertRaises(ValueError, setattr, obs, 'v', str(badEnd))
             
            badDefault = max + 1
             
        else:
            end = 100
             
        endStr = str(end)
        obs.v = endStr
        self.assertEqual(obs.v, endStr)
         
        n = 10
        for i in range(n):
            v = str(start + (end - start) / float(n - 1) * i)
            obs.v = v
            self.assertEqual(obs.v, v)
             
        if badDefault is not None:
            self._assertRaises(
                ValueError, Decimal,
                **{'min': minStr, 'max': maxStr, 'default': str(badDefault)})
