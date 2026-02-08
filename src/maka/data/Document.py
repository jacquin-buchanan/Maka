from maka.data.EditHistory import Edit, EditHistory


class Document(object):
    
    
    extensionName = None            # string, more human-friendly than class name
    observationClasses = None       # set, useful for constructing document formats
    fieldClasses = None             # set, useful for constructing document formats
    
    
    '''
    Want to be able to extend the application with new edit operations. An edit
    operation will take a document, a selection, and possibly other information
    collected from a GUI and modify the document. The operation may or may not
    use the selection. An edit operation will have a name (e.g. "Cut" or "Reduce"),
    a shortcut, a tip, and a description.
    '''
    
    
    def __init__(
        self, observations=None, documentFormat=None, fileFormat=None, filePath=None,
        edited=False):
        
        super(Document, self).__init__()
        
        self.observations = [] if observations is None else observations
        self.documentFormat = documentFormat
        self.fileFormat = fileFormat
        self.filePath = filePath
        self.edited = edited
        
        self._editHistory = EditHistory()
        self._editListeners = set()


    def addEditListener(self, listener):
        self._editListeners.add(listener)
        
        
    def removeEditListener(self, listener):
        self._editListeners.remove(listener)
        
        
    def _notifyEditListeners(self, edit):
        for listener in self._editListeners:
            listener(edit)


    def edit(self, name, startIndex, endIndex, observations):
        
        edit = DocumentEdit(name, self, startIndex, endIndex, observations)
        edit.do()
    
        self._editHistory.append(edit)
        self._notifyEditListeners(edit)
        
        
    @property
    def saved(self):
        return self._editHistory.documentSaved
    
    
    def markSaved(self):
        self._editHistory.markDocumentSaved()
        
        
    @property
    def undoName(self):
        return self._editHistory.undoName
        
    
    @property
    def redoName(self):
        return self._editHistory.redoName
        
        
    def undo(self):
        edit = self._editHistory.undo()
        self._notifyEditListeners(edit)
        return edit
        
        
    def redo(self):
        edit = self._editHistory.redo()
        self._notifyEditListeners(edit)
        return edit


class DocumentEdit(Edit):
    
    
    def __init__(self, name, document, startIndex, endIndex, observations):
        
        super(DocumentEdit, self).__init__(name)
        
        _checkEditIndices(startIndex, endIndex, len(document.observations))
        
        self._document = document
        self._startIndex = startIndex
        self._endIndex = endIndex
        self.oldObservations = _copy(document.observations, startIndex, endIndex)
        self.newObservations = _copy(observations, 0, len(observations))
        
        
    @property
    def document(self):
        return self._document
    
    
    @property
    def startIndex(self):
        return self._startIndex
    
    
    @property
    def endIndex(self):
        return self._endIndex
    
    
    @property
    def inverse(self):
        name = self.name + ' Inverse'
        startIndex = self.startIndex
        endIndex = startIndex + len(self.newObservations)
        return DocumentEdit(name, self.document, startIndex, endIndex, self.oldObservations)
        
        
    def do(self):
        self.document.observations[self.startIndex:self.endIndex] = \
            _copy(self.newObservations, 0, len(self.newObservations))
        
        
def _checkEditIndices(startIndex, endIndex, maxIndex):
    
    _checkEditIndex(startIndex, maxIndex, 'start')
    _checkEditIndex(endIndex, maxIndex, 'end')
    
    if endIndex < startIndex:
        raise ValueError('Edit end index must be at least start index.')
    
    
def _checkEditIndex(index, maxIndex, name):
    
    if index < 0:
        raise ValueError('Edit {:s} index must be at least zero.'.format(name))
    
    if index > maxIndex:
        raise ValueError('Edit {:s} index must not exceed document length.'.format(name))
        

def _copy(observations, startIndex, endIndex):
    return tuple(observations[i].copy() for i in range(startIndex, endIndex))
