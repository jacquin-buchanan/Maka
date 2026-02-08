from __future__ import print_function

from maka.data.Document import Document
from maka.data.Field import Integer
from maka.data.Observation import Observation

from MakaTests import TestCase

    
class Obs(Observation):
    x = Integer
    
    
def _createObservations(ints):
    return [Obs(x=i) for i in ints]
    
    
class DocumentTests(TestCase):
    
    
    def setUp(self):
        self.document = Document()
        self.document.addEditListener(self.editListener)
        self.edit = None
        
        
    def testEditNameAndNotification(self):
        name = 'Bobo'
        self.document.edit(name, 0, 0, [])
        self.assertEqual(self.edit.name, name)
        
        
    def testEdit(self):
        
        cases = [
            (0, 0, [0, 1, 2, 3], [0, 1, 2, 3]),
            (0, 0, [10, 11], [10, 11, 0, 1, 2, 3]),
            (0, 2, [], [0, 1, 2, 3]),
            (0, 2, [10], [10, 2, 3]),
            (0, 1, [11, 12], [11, 12, 2, 3]),
            (0, 2, [0, 1], [0, 1, 2, 3]),
            (1, 3, [10, 11, 12], [0, 10, 11, 12, 3]),
            (1, 4, [1, 2], [0, 1, 2, 3]),
            (4, 4, [], [0, 1, 2, 3]),
            (4, 4, [10, 11], [0, 1, 2, 3, 10, 11])
        ]
        
        for i, n, ints, expected in cases:
            self._edit(i, n, ints)
            self._assertObservations(expected)
            
            
    def _edit(self, i, n, ints):
        obses = _createObservations(ints)
        self.document.edit('Edit', i, n, obses)
        
        
    def testEditErrors(self):
        
        self._edit(0, 0, [0, 1, 2, 3])
        
        cases = [
            (-1, 0),
            (0, -1),
            (5, 5),
            (4, 5),
            (4, 3)
        ]
        
        for i, n in cases:
            self._assertRaises(ValueError, self.document.edit, 'Edit', i, n, [])
            
            
    def _assertObservations(self, ints):
        obses = self.document.observations
        self.assertEqual(len(obses), len(ints))
        for i in range(len(ints)):
            self.assertEqual(obses[i].x, ints[i])
        
        
    def editListener(self, edit):
        self.edit = edit
