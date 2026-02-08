'''Manages application extensions.'''


'''
extension classes:

Field
Observation
Document

FieldFormat
ObservationFormat
DocumentFormat

DocumentFileFormat

Device

Perhaps every extension class should be a subclass of an `Extension` class.
'''


_extensions = None
'''mapping from extension type names to sets of extensions.'''


def _initializeIfNeeded():
    
    global _extensions
    
    if _extensions is not None:
        return
        
    _extensions = {}
    
    from maka.format.MakaDocumentFileFormat import MakaDocumentFileFormat
    _addExtensions('DocumentFileFormat', [MakaDocumentFileFormat])
    
    from maka.mmrp.MmrpDocumentFormat101 import MmrpDocumentFormat101
    _addExtensions('DocumentFormat', [MmrpDocumentFormat101])
    
    from maka.mmrp.MmrpCommandInterpreter101 import MmrpCommandInterpreter101
    _addExtensions('CommandInterpreter', [MmrpCommandInterpreter101])
    
    from maka.device.SokkiaTheodolite import SokkiaDt4Theodolite, SokkiaDt500Theodolite
    from maka.device.DummyTheodolite import DummyTheodolite
    _addExtensions('Device', [DummyTheodolite, SokkiaDt4Theodolite, SokkiaDt500Theodolite])
    
    
def _addExtensions(typeName, extensions):
    global _extensions
    _extensions[typeName] = dict((e.extensionName, e) for e in extensions)


def getExtension(typeName, extensionName):
    _initializeIfNeeded()
    return _extensions.get(typeName, {}).get(extensionName)


def getExtensions(typeName):
    _initializeIfNeeded()
    return frozenset(_extensions.get(typeName, {}).values())
