from maka.data.EditHistory import Edit, EditHistory

from MakaTests import TestCase

    
class ListEdit(Edit):
    
    
    def __init__(self, name, list, index, oldValue, newValue):
        super(ListEdit, self).__init__(name)
        self._list = list
        self._index = index
        self._oldValue = oldValue
        self._newValue = newValue
        
        
    @property
    def inverse(self):
        return ListEdit(
            self.name + ' inverse', self._list, self._index, self._newValue, self._oldValue)
        
        
    def do(self):
        self._list[self._index] = self._newValue
        
    
class EditHistoryTests(TestCase):
    
    
    def setUp(self):
        self._history = EditHistory()
        self._nums = list(range(4))
        self._assertState(None, None, list(range(4)))
        
        
    def _assertState(self, undoName, redoName, nums):
        h = self._history
        self.assertEqual(h.undoName, undoName)
        self.assertEqual(h.redoName, redoName)
        self.assertEqual(self._nums, nums)
        
        
    def testUndoRedo(self):
        
        h = self._history
        
        self._edit('one', 1, 21)
        self._assertState('one', None, [0, 21, 2, 3])
        
        h.undo()
        self._assertState(None, 'one', list(range(4)))
        
        h.redo()
        self._assertState('one', None, [0, 21, 2, 3])
        
        self._edit('two', 3, 23)
        self._edit('three', 1, 19)
        self._assertState('three', None, [0, 19, 2, 23])
        
        h.undo()
        self._assertState('two', 'three', [0, 21, 2, 23])
        
        h.undo()
        self._edit('four', 0, 20)
        self._assertState('four', None, [20, 21, 2, 3])
        
        
    def _edit(self, name, i, n):
        nums = self._nums
        edit = ListEdit(name, nums, i, nums[i], n)
        edit.do()
        self._history.append(edit)
        
        
    def testUndoRedoErrors(self):
        h = self._history
        self._assertRaises(IndexError, h.undo)
        self._assertRaises(IndexError, h.redo)
        
        
    def testMarkDocumentSaved(self):
        
        h = self._history
        
        self.assertTrue(h.documentSaved)
        
        self._edit('one', 1, 21)
        self.assertFalse(h.documentSaved)
        
        h.undo()
        self.assertTrue(h.documentSaved)
        
        h.redo()
        self.assertFalse(h.documentSaved)
        
        h.markDocumentSaved()
        self.assertTrue(h.documentSaved)
        
        h.undo()
        self.assertFalse(h.documentSaved)
        
        h.redo()
        self.assertTrue(h.documentSaved)
        
        self._edit('two', 2, 22)
        self.assertFalse(h.documentSaved)
        
        h.undo()
        self.assertTrue(h.documentSaved)
        
        h.undo()
        self.assertFalse(h.documentSaved)
        
        h.markDocumentSaved()
        self.assertTrue(h.documentSaved)

        h.redo()
        self.assertFalse(h.documentSaved)
        
        h.redo()
        self.assertFalse(h.documentSaved)
        
