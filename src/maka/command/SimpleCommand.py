from maka.command.CommandInterpreterError import CommandInterpreterError


class SimpleCommand(object):
    
    
    observationClass = None
    '''the class of the observations created by this command.'''
    

    format = None
    '''
    the format of this command.
    
    A command format comprises a *command name* followed by zero or more
    *field names*, all separated by spaces. For example::
    
        'cmd x y'
        
    is the format of a command named `'cmd'` with the two field names
    `'x'` and `'y'`. The field names must be the names of fields of
    observations of type `observationClass`.
    '''
    
    defaultFieldValues = {}
    '''
    the default field values of this command, a dictionary mapping field
    names and tuples of field names to default values.
    
    A default field value may be specified either as a value of the appropriate
    type or as a callable. A callable must take a single argument, a command
    interpreter, and return a value of the appropriate type.
    
    Default values for multiple fields may be specified by a dictionary
    entry whose key is a tuple of field names and whose value is either a
    tuple of values of the appropriate types or a callable that takes
    a command interpreter and returns such a tuple.
    
    Default field values for a command may be specified not only via the
    `defaultFieldValues` attribute of the command's class, but also via
    the `defaultFieldValues` attributes of its ancestor classes. The
    specified dictionaries are combined when a command instance is
    initialized so that when the command is executed the dictionaries
    are effectively consulted for default field values in accordance with
    the command class's method resolution order (MRO).
    '''
    
    
    def __init__(self, interpreter):
        
        super(SimpleCommand, self).__init__()
        
        (self._name, self._fieldNames) = self._parseFormat()
        self._maxNumArgs = len(self._fieldNames)
        
        self._accumulateDefaultFieldValues()
        
        self._interpreter = interpreter
        
        obsClassName = self.observationClass.__name__
        self._obsFormat = self._interpreter._docFormat.getObservationFormat(obsClassName)

        
    def _parseFormat(self):
        
        parts = self.format.split()
        
        commandName = parts[0]
        argNames = parts[1:]
        
        self._checkCommandArgNames(argNames, commandName)
        
        return commandName, argNames
        
        
    def _checkCommandArgNames(self, argNames, commandName):
        
        fieldNames = frozenset(field.name for field in self.observationClass.FIELDS)
        
        for name in argNames:
            if name not in fieldNames:
                raise CommandInterpreterError(
                    ('Bad argument name "{:s}" in command "{:s}" format. Argument '
                     'name must be field name for observation type "{:s}".').format(
                        name, commandName, self.observationClass.__name__))
                                              
    
    def _accumulateDefaultFieldValues(self):
        
        # TODO: Check field names and values in `cls.defaultFieldValues` in the following.
        
        self._defaultFieldValues = {}

        for cls in reversed(self.__class__.__mro__[:-1]):
            
            try:
                defaultFieldValues = cls.defaultFieldValues
            except AttributeError:
                continue
            
            self._defaultFieldValues.update(defaultFieldValues)
        
       
    @property
    def name(self):
        return self._name
    
                         
    def __call__(self, *args):
        fieldValues = self._getFieldValues(args)
        return self.observationClass(**fieldValues)
    
    
    def _checkNumArgs(self, args):
        
        if len(args) > self._maxNumArgs:
            
            if self._maxNumArgs == 0:
                message = 'Command "{:s}" takes no arguments.'.format(self.name)
            else:
                message = 'Too many arguments for command "{:s}": maximum number is {:d}.'.format(
                              self.name, self._maxNumArgs)
                
            raise CommandInterpreterError(message)
        
        
    def _getFieldValues(self, args):
        
        fieldValues = dict(self._parseArg(arg, i) for i, arg in enumerate(args))
        
        for key, value in self._defaultFieldValues.items():
            
            if isinstance(key, tuple):
                # key is tuple of field names
                
                names = [name for name in key if name not in fieldValues]
                
                if len(names) != 0:
                    # At least one of the named fields does not yet have a value.
                    # We guard the following with this test to avoid invoking callables
                    # to get field values that are not needed. This is particularly
                    # important for stateful callables such as serial number generators.
                    
                    values = value(self._interpreter) if callable(value) else value
                        
                    for i, name in enumerate(key):
                        if name not in fieldValues:
                            fieldValues[name] = values[i]
                            
            else:
                # key is a single field name
                
                if key not in fieldValues:
                    # named field does not yet have a value
                    
                    fieldValues[key] = value(self._interpreter) if callable(value) else value
                    
        # TODO: Combine callable value and field values hook mechanisms?
        return self._fieldValuesHook(fieldValues)
                
                        
    def _parseArg(self, arg, i):
        
        fieldName = self._fieldNames[i]
        fieldFormat = self._obsFormat.getFieldFormat(fieldName)
        
        try:
            value = fieldFormat.parse(arg)
            
        except ValueError as e:
            raise CommandInterpreterError(
                'Could not parse "{:s}" argument for command "{:s}". {:s}'.format(
                    fieldName, self.name, str(e)))
            
        return fieldName, value
    
    
    def _fieldValuesHook(self, fieldValues):
        return fieldValues
    
