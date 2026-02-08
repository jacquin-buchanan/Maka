from maka.data.Document import Document
from maka.format.DocumentFileFormat import (
    DocumentFileFormat, FileFormatError, UnrecognizedFileFormatError)
import maka.util.ExtensionManager as ExtensionManager


# For the time being we retain "aardvark data" rather than switching to "maka data"
# since we want to be able to open Maka MMRP data files in the Aardvark Viewer.
# We can switch to "maka data" when the Aardvark Viewer is no longer needed.
_FIRST_HEADER_LINE = 'aardvark data'

_GRAMMAR_PREFIX = 'grammar '
_FORMAT_PREFIX = 'format '


'''
aardvark data
grammar "'96 MMRP Grammar 1.01"

aardvark data
format HMMC Document Format 0.01
'''
    
    
class MakaDocumentFileFormat(DocumentFileFormat):
    
    
    extensionName = 'Maka Document File Format'
    
    
    def isFileRecognized(self, filePath):
        with _openTextFile(filePath) as file:
            try:
                _checkFileHeader(file, filePath)
            except UnrecognizedFileFormatError:
                return False
            else:
                return True
        
        
    def readDocument(self, filePath):
        
        with _openTextFile(filePath) as file:
            
            _checkFileHeader(file, filePath)
            (docFormat, lineNum) = _getDocFormat(file, filePath)
                
            lines = file.read().splitlines()
        
        try:
            observations = docFormat.parseDocument(lines, lineNum)
        except ValueError as e:
            e.filePath = filePath
            raise
            
        document = Document(
            observations,
            documentFormat=docFormat,
            fileFormat=self,
            filePath=filePath)
        
        return document
    
    
    def writeDocument(self, document, filePath, documentFormat):
        
        # TODO: Handle I/O exceptions.
        with open(filePath, 'w') as file:
            
            _writeHeader(file, documentFormat)
            
            # TODO: Handle format exceptions.
            file.write(documentFormat.formatDocument(document.observations))

            
def _checkFileHeader(file, filePath):
    if file.readline().strip() != _FIRST_HEADER_LINE:
        raise UnrecognizedFileFormatError(
            'File "{:s}" does not start with Maka data file header.'.format(filePath))
                    
            
def _getDocFormat(file, filePath):
    
    line = file.readline().strip()
    
    # TODO: Always quote grammar/format name?
    
    if line.startswith(_GRAMMAR_PREFIX):
        name = line[len(_GRAMMAR_PREFIX):].strip()
        if name.startswith('"') and name.endswith('"'):
            name = name[1:-1]
        return _getDocFormatAux(name, 'Grammar', 2, filePath)
        
    elif line.startswith(_FORMAT_PREFIX):
        name = line[len(_FORMAT_PREFIX):].strip()
        return _getDocFormatAux(name, 'Format', 2, filePath)
    
    else:
        _raiseFileFormatError('Format specification', 2, filePath)

                
def _openTextFile(filePath):  
    
    # We open the file with universal newlines support so that we will correctly
    # recognize lines whether they are terminated with '\n' (the Unix convention),
    # '\r' (the old Macintosh convention), or '\r\n' (the Windows convention).
    return open(filePath, 'U')  


def _raiseFileFormatError(prefix, lineNum, filePath):
    raise FileFormatError(
        '{:s} missing at line {:d} of Maka data file "{:s}".'.format(
            prefix, lineNum, filePath))
    
    
def _getDocFormatAux(name, messagePrefix, lineNum, filePath):
    
    if name == '':
        _raiseFileFormatError(messagePrefix + ' name', lineNum, filePath)

    formatClass = _getExtension('DocumentFormat', name, 'document format', lineNum, filePath)
        
    return (formatClass(), lineNum)


def _getExtension(typeName, extensionName, description, lineNum, filePath):
    
    extension = ExtensionManager.getExtension(typeName, extensionName)
    
    if extension is None:
        raise ValueError(
            'Unknown {:s} "{:s}" specified at line {:d} of Maka data file "{:s}".'.format(
                description, extensionName, lineNum, filePath))
        
    else:
        return extension


def _writeHeader(file, docFormat):
    formatLine = '{:s}"{:s}"'.format(_GRAMMAR_PREFIX, docFormat.extensionName)
    file.write('{:s}\n{:s}\n\n'.format(_FIRST_HEADER_LINE, formatLine))
