from __future__ import print_function

import os

import maka.util.ExtensionManager as ExtensionManager


'''
Because observation fields are implemented using Python descriptors, they are a little odd.
I would like, however, to have a solid language-independent model of Maka data and
understand how that is implemented in Python. How would I model Maka data in other
languages, such as JSON, Scala, and C++?

field type - name, set of allowed values, default value
field - name, field type, and value

observation type - name, sequence of (field name, field type) pairs
observation - mapping from field names to field values

document type - set of field and observation types
document - sequence of observations, associated file path

Observation types are implemented as Python classes, and observations as instances
of these classes. Field types are implemented as Python descriptor class instances.
A field type descriptor class provides type and range checking functionality, and
an instance has attributes that determine the field value range and default value.
A field type descriptor instance is a class attribute of an *owning* observation
class, for which it mediates read and write access to a particular field for
instances of the observation class.

field format - formats and parses values of one or more field types
observation format - formats and parses observations of one or more observation types
document format - formats and parses documents of one or more document types

One of the goals of Maka is to separate the specification of types from formats as much
as is practical. This will make it easier to support multiple formats for a given field
type, observation type, or document type.

Questions:

* Should there be `Document` and/or `DocumentType` classes?

* How to support extensibility involving field, observation, and document types and formats?
'''


'''
Plugins

application, component, core, extension, extension type, plugin

An *application* comprises one or more *components*. The components include exactly
one *core* component and zero or more *extension* components. An *extension type* is a
contract defined by a component (either the core or an extension) that another component
(an extension) satisfies in order to extend it. Each extension satisfies the contract
of one or more extension types, and is said to *implement* those extension types.

Execution commences in the core, which assembles an application by locating all of its
components and connecting them to each other. A *plugin* is a set of extensions 
that are distributed as a single Python package. This package is placed in the *plugins*
package of an application so the core can discover it. A plugin declares in its __init__
module the extensions it contains (how, exactly, is TBD), and modules within a plugin
package implement the extensions. Each extension indicates (somehow, TBD) the extension
types it implements as well as the extension types it defines.

Perhaps extension types should be Python classes and extensions should implement them?

We could automatically locate extensions by searching all of the modules of a plugin for
subclasses of extension types. This requires importing all of the modules at startup,
however. This might be undesirable for large applications, though for small ones I suspect
it would not be a problem.

For some applications, it may happen that most extensions are not actually instantiated
during the execution of a program, so that it would be wasteful to import all modules
associated with all extensions at startup. Can we make it easy to defer importing many
modules until they are actually needed?

In some cases an application will not be extended. Can we reduce startup time using
frozen modules or something similar?


class Extension(object):

    def __init__(self, name):
        self.name = name
        
        
class DocumentTypeExtension(Extension):

    ???


plugins package

    plugin package
        __init__.py
            list of extension classes
        packages and modules including extension classes
            
    etc.
'''
    

HMMC_DATA_DIR_PATH = '/Users/Harold/Desktop/Stuff/Maka/HMMC 2013/Data'
TEMP_FILE_PATH = '/Users/Harold/Desktop/Stuff/Maka/Temp.txt'


def main():
    
    fileFormat = ExtensionManager.getExtension('DocumentFileFormat', 'Maka Document File Format')()
    docFormat = ExtensionManager.getExtension('DocumentFormat', "'96 MMRP Grammar 1.01")()

    for dirPath, _, fileNames in os.walk(HMMC_DATA_DIR_PATH):
        
        for fileName in fileNames:
            
            filePath = os.path.join(dirPath, fileName)
            
            if fileFormat.isFileRecognized(filePath):
        
                print('processing file "{:s}"...'.format(filePath))
                
                try:
                    document = fileFormat.readDocument(filePath)
                except ValueError as e:
                    try:
                        getattr(e, 'line_num')
                    except AttributeError:
                        print('Error parsing file "{:s}": {:s}'.format(filePath, str(e)))
                    else:
                        print('Parse error at line {:d} of file "{:s}": {:s}'.format(
                                  e.line_num, filePath, str(e)))

                
                fileFormat.writeDocument(document, TEMP_FILE_PATH, docFormat)
                
                document2 = fileFormat.readDocument(TEMP_FILE_PATH)
               
                if document.observations != document2.observations:
                    observations = document.observations
                    observations2 = document2.observations
                    print('>>>>>>>>>> Format test failed for file "{:s}".'.format(filePath))
                    if len(observations) != len(observations2):
                        print('    Numbers of observations differ.')
                    else:
                        for i, (a, b) in enumerate(zip(observations, observations2)):
                            if a != b:
                                print('    Observations {:d} differ.'.format(i))
                                print('    ' + docFormat.format([observations[i]]))
                                print('    ' + docFormat.format([observations2[i]]))
                                break


if __name__ == '__main__':
    main()
    