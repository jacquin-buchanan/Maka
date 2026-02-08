from __future__ import print_function

import datetime

from maka.data.Field import Float, Integer, String
from maka.data.Observation import Observation
from maka.format.SimpleDocumentFormat import (
    AngleFormat, DateFormat, DecimalFormat, FloatFormat, IntegerFormat, SimpleObservationFormat,
    StringFormat, TimeFormat)
from maka.util.TokenUtils import NONE_TOKEN as FORMATTED_NONE

from MakaTests import TestCase


_EDITING_NONE = ''


_STRING_CASES = [
    ('Hello', 'Hello'),
    ('Hello, world!', '"Hello, world!"'),
    ('\\', '"\\\\"'),
    ('"', '"\\""'),
    ('\\"', '"\\\\\\""'),
    ('"\\', '"\\"\\\\"'),
    ('""', '"\\"\\""'),
    ('"Hello \\ World!"', '"\\"Hello \\\\ World!\\""')
]


_DECIMAL_CASES = [(s, s) for s in [
    '0', '-0', '12', '-123', '0.', '12.', '-0.', '12.', '1.2', '-1.2', '.1', '-.1'
]]


_INTEGER_CASES = [
    (0, '0'),
    (12, '12'),
    (-123, '-123')
]


_FLOAT_CASES = [
    (0, '0'),
    (12, '12'),
    (-123, '-123'),
    (.1, '0.1'),
    (1.2, '1.2'),
    (-.1, '-0.1'),
    (-1.2, '-1.2'),
    (1.23456, '1.23456'),
    (1.23456789, '1.23456789'),
    (1.234567891234567, '1.234567891234567')
]


_ANGLE_CASES = [
    (0, '0:00:00'),
    (1, '1:00:00'),
    (1.25, '1:15:00'),
    (1 + 30 / 3600., '1:00:30'),
    (1 + 15 / 60. + 30 / 3600., '1:15:30'),
    (90, '90:00:00'),
    (360, '360:00:00'),
    (-1.5, '-1:30:00')
]


_DATE_CASES = [
    ((1970, 1, 2), '1/2/70'),
    ((2013, 1, 2), '1/2/13'),
    ((2013, 10, 1), '10/1/13'),
    ((2013, 1, 10), '1/10/13'),
    ((2013, 10, 11), '10/11/13'),
    ((1970, 1, 1), '1/1/70'),
    ((2069, 12, 31), '12/31/69')
]


_TIME_CASES = [
    ((0, 0, 0), '0:00:00'),
    ((23, 59, 59), '23:59:59'),
    ((1, 23, 45), '1:23:45')
]


class Obs(Observation):
    f = Float(default=1.23)
    i = Integer(default=2)
    s = String(default='Hello')
    
    
class FormatTests(TestCase):
    
    
    def _testFieldFormat(self, f, cases):
        self._testFieldFormatNone(f)
        for value, formattedValue in cases:
            self._testFieldFormatAux(
                f, [(value, False, formattedValue), (value, True, formattedValue)])
            
            
    def _testFieldFormatNone(self, f):
        self._testFieldFormatAux(f, [(None, False, FORMATTED_NONE), (None, True, _EDITING_NONE)])


    def _testFieldFormatAux(self, f, cases):
        for case in cases:
            if len(case) == 2:
                value, formattedValue = case
                self.assertEqual(f.format(value, editing=False), formattedValue)
                self.assertEqual(f.format(value, editing=True), formattedValue)
            else:
                value, editing, formattedValue = case
                self.assertEqual(f.format(value, editing=editing), formattedValue)
                
        
    def _testFieldParse(self, f, cases):
        self._testFieldParseNone(f)
        for formattedValue, value in cases:
            self._testFieldParseAux(
                f, [(formattedValue, False, value), (formattedValue, True, value)])
        
        
    def _testFieldParseNone(self, f):
        self._testFieldParseAux(f, [(FORMATTED_NONE, False, None), (_EDITING_NONE, True, None)])
        
        
    def _testFieldParseAux(self, f, cases):
        for case in cases:
            if len(case) == 2:
                formattedValue, value = case
                self.assertEqual(f.parse(formattedValue, editing=False), value)
                self.assertEqual(f.parse(formattedValue, editing=True), value)
            else:
                formattedValue, editing, value = case
                self.assertEqual(f.parse(formattedValue, editing=editing), value)
            
            
    def _testFieldParseErrors(self, f, cases):
        self._testFieldParseErrorsNone(f)
        self._testFieldParseErrorsAux(f, cases)
            
            
    def _testFieldParseErrorsNone(self, f):
        self._testFieldParseErrorsAux(f, [(FORMATTED_NONE, True), (_EDITING_NONE, False)])
        
        
    def _testFieldParseErrorsAux(self, f, cases):
        for case in cases:
            if isinstance(case, tuple):
                formattedValue, editing = case
                self.assertRaises(ValueError, f.parse, formattedValue, editing)
            else:
                self.assertRaises(ValueError, f.parse, case, False)
                self.assertRaises(ValueError, f.parse, case, True)
                
                
    def testStringFormat(self):
        
        f = StringFormat()
        
        self._testFieldFormatNone(f)

        cases = _STRING_CASES + [
                         
            # The empty string should be formatted with quotes, even though quotes are parsed
            # as `None`.
            # TODO: Add this case to `_STRING_CASES` when `FORMATTED_NONE` is no longer `'""'`.        
            ('', '""')
            
        ]
        
        for value, formattedValue in cases:
            self._testFieldFormatAux(f, [(value, False, formattedValue), (value, True, value)])
        
    
    def testStringParse(self):
        
        f = StringFormat()
        
        self._testFieldParseNone(f)
        
        cases = _swap(_STRING_CASES) + [
            
            # While a string with no whitespace, backslashes, or quotes is formatted
            # without surrounding quotes, if the quotes are added we should still
            # parse the string by stripping the quotes.
            ('"Hello"', 'Hello')
            
        ]
        
        for formattedValue, value in cases:
            self._testFieldParseAux(f, [(formattedValue, False, value), (value, True, value)])
        
        
    def testDecimalFormat(self):
        self._testFieldFormat(DecimalFormat(), _DECIMAL_CASES)
        
        
    def testDecimalParse(self):
        self._testFieldParse(DecimalFormat(), _swap(_DECIMAL_CASES))
        
        
    def testDecimalParseErrors(self):
        self._testFieldParseErrors(DecimalFormat(), [
            'bobo', '--1', '1-2', '10:20:30', '10-', '..1', '1..'
        ])
        
        
    def testIntegerFormatReplacementFieldErrors(self):
        self._assertRaises(ValueError, IntegerFormat, '{:d')
        self._assertRaises(ValueError, IntegerFormat, '{d}')
        
        
    def testIntegerFormat(self):
        self._testFieldFormat(IntegerFormat(), _INTEGER_CASES)
            
            
    def testIntegerFormatWithReplacementField(self):
        self._testFieldFormat(IntegerFormat('{:05d}'), [
            (0, '00000'),
            (12, '00012')
        ])
        
        
    def testIntegerParse(self):
        self._testFieldParse(IntegerFormat(), _swap(_INTEGER_CASES) + [('-0', 0)])

        
    def testIntegerParseErrors(self):
        self._testFieldParseErrors(IntegerFormat(), [
            'bobo', '1.2', '--1', '1-2', '10:20:30'
        ])
        
        
    def testFloatFormatReplacementFieldErrors(self):
        self._assertRaises(ValueError, FloatFormat, '{:f')
        self._assertRaises(ValueError, FloatFormat, '{f}')
        
        
    def testFloatFormat(self):
        self._testFieldFormat(FloatFormat(), _FLOAT_CASES + [
                                
            # Here we lose some precision because of the finite precision of floats.
            (1.2345678912345678, '1.234567891234568')
            
        ])

        
    def testFloatFormatWithReplacementField(self):
        self._testFieldFormat(FloatFormat('{:.5f}'), [
            (0, '0.00000'),
            (1.23456789, '1.23457')
        ])
        
        
    def testFloatParse(self):
        self._testFieldParse(FloatFormat(), _swap(_FLOAT_CASES) + [
                                
            ('-0', 0),
            
            # Decimal numbers with magnitudes less than one and no leading zero.
            ('.1', .1),
            ('-.1', -.1),
            
            # Here we lose some precision because of the finite precision of floats.
            ('1.2345678912345678', 1.234567891234568)
            
        ])

        
    def testFloatParseErrors(self):
        self._testFieldParseErrors(FloatFormat(), [
            'bobo', '1.2.3', '--1', '1-2', '10:20:30'
        ])
        
        
    def testAngleFormat(self):
        self._testFieldFormat(AngleFormat(), _ANGLE_CASES + [
                                                
            # Some floats rounded to four fractional digits.
            (1.0083, '1:00:30'),
            (1.2583, '1:15:30'),
            
            # Regression test for bug discovered 2013-08-26.
            (0.01666666666, '0:01:00')          # bug caused result of '0:00:60'
            
        ])
        
        
    def testAngleParse(self):
        self._testFieldParse(AngleFormat(), _swap(_ANGLE_CASES))
        
        
    def testAngleParseErrors(self):
        self._testFieldParseErrors(AngleFormat(), [
            'bobo', '1.2.3', '--1', '1-2', '1.2', '10', '10:20', '10:20:30:40'
        ])
        
        
    def testDateFormat(self):
        cases = [(datetime.date(*triple), s) for triple, s in _DATE_CASES]
        self._testFieldFormat(DateFormat(), cases)
        
        
    def testDateParse(self):
        cases = [(s, datetime.date(*triple)) for triple, s in _DATE_CASES]
        self._testFieldParse(DateFormat(), cases)
       
        
    def testDateParseErrors(self):
        self._testFieldParseErrors(DateFormat(), [
            'bobo', '1', '1/2', '1/2/3/4', '1:23:45', '0/1/13', '13/1/13',
            '1/0/13', '1/32/13', '2/30/12', '1/2/12345'
        ])
        
        
    def testTimeFormat(self):
        cases = [(datetime.time(*triple), s) for triple, s in _TIME_CASES]
        self._testFieldFormat(TimeFormat(), cases)
        
        
    def testTimeParse(self):
        cases = [(s, datetime.time(*triple)) for triple, s in _TIME_CASES]
        self._testFieldParse(TimeFormat(), cases)
       
        
    def testTimeParseErrors(self):
        self._testFieldParseErrors(TimeFormat(), [
            'bobo', '1', '1:2', '1:2:3:4', '1/23/45', '-1:00:00', '0:-1:00', '0:00:-1',
            '0:0:00', '0:00:0', '000:00:00', '0:000:00', '0:00:000', '24:00:00', '0:60:00',
            '0:00:60'
        ])
        
        
    def testSimpleObservationFormat(self):
        
        from  maka.mmrp.MmrpDocumentFormat101 import _fieldFormats
        
        obs = Obs()
        
        cases = [
            ('float* {f} integer {i} string {s}', (0, 'float 1.23 integer 2 string Hello')),
            ('integer {i} float* {f}', (2, 'integer 2 float 1.23')),
            ('one two {i:05d} three* {f:.3f}', (3, 'one two 00002 three 1.230'))
        ]
        
        for formatSpec, (keyIndex, s) in cases:
            f = SimpleObservationFormat(formatSpec, Obs, _fieldFormats)
            self.assertEqual(f.keyIndex, keyIndex)
            self.assertEqual(f.formatObservation(obs), s)


    def testSimpleObservationFormatErrors(self):
        
        from  maka.mmrp.MmrpDocumentFormat101 import _fieldFormats
        
        cases = ['{f]', '{{f}', 'float {f}']
        
        for case in cases:
            self._assertRaises(ValueError, SimpleObservationFormat, case, Obs, _fieldFormats)
        
        
    def testObsParse(self):
        
        import maka.mmrp.MmrpDocumentFormat101 as mmrpDocFormat
        
        f = SimpleObservationFormat(
            'float* {f} integer {i} string {s}', Obs, mmrpDocFormat._fieldFormats)
        
        cases = [
            ('float 1.23 integer 2 string "Hello"', {'f': 1.23, 'i': 2, 's': 'Hello'})
        ]
        
        for s, d in cases:
            obs = f.parseObservation(s)
            for k, v in d.items():
                self.assertEqual(getattr(obs, k), v)
                
                
    def testFormatAndParseDocument(self):
        
        from datetime import date, time
        from maka.mmrp.MmrpDocument101 import Fix, Pod
        from maka.mmrp.MmrpDocumentFormat101 import MmrpDocumentFormat101
        
        observations = [
            Pod(id=1, numWhales=2, numCalves=1, numSingers=0),
            Fix(observationNum=10, date=date(2013, 2, 1), time=time(1, 23, 45), declination=91,
                azimuth=2.5, objectType='Pod', objectId=1),
            Fix(observationNum=11, date=date(2013, 2, 1), time=time(1, 23, 50), declination=91,
                azimuth=2.75, objectType='Pod', objectId=1)]

        formattedObservations = [
            'Pod 1 Whales 2 Calves 1 Singers 0',
            '00010 2/1/13 1:23:45 Fix Dec 91:00:00 Az 2:30:00 Pod 1 State ""',
            '00011 2/1/13 1:23:50 Fix Dec 91:00:00 Az 2:45:00 Pod 1 State ""'
        ]
        
        formattedDocument = ''.join([obs + '\n' for obs in formattedObservations])
        
        f = MmrpDocumentFormat101()
        self.assertEqual(f.formatDocument(observations), formattedDocument)
        self.assertEqual(f.parseDocument(formattedObservations), observations)
        
        
    def testFormatObservation(self):
        
        from maka.mmrp.MmrpDocument101 import Pod
        from maka.mmrp.MmrpDocumentFormat101 import MmrpDocumentFormat101
        
        obs = Pod(id=1, numWhales=2, numCalves=1, numSingers=0)
        formattedObs = 'Pod 1 Whales 2 Calves 1 Singers 0'
        
        f = MmrpDocumentFormat101()
        self.assertEqual(f.formatObservation(obs), formattedObs)
        
        
    def testFormatFieldValue(self):

        from maka.mmrp.MmrpDocument101 import Pod
        from maka.mmrp.MmrpDocumentFormat101 import MmrpDocumentFormat101
        
        obs = Pod(id=1, numWhales=2, numCalves=1, numSingers=0)
        
        f = MmrpDocumentFormat101().getObservationFormat(obs.__class__.__name__)
        self.assertEqual(f.formatFieldValue('numWhales', obs), '2')
        
        
    def testFieldOrder(self):
        from maka.mmrp.MmrpDocumentFormat101 import MmrpDocumentFormat101
        obsClassName = 'Pod'
        f = MmrpDocumentFormat101().getObservationFormat(obsClassName)
        self.assertEqual(f.fieldOrder, ('id', 'numWhales', 'numCalves', 'numSingers'))
        
        
def _swap(pairs):
    return [(b, a) for (a, b) in pairs]
