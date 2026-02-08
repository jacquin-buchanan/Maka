'''Module containing `CommandInterpreter` class.'''


import re

from maka.command.CommandInterpreterError import CommandInterpreterError
import maka.util.TokenUtils as TokenUtils


class SimpleCommandInterpreter(object):
    
    '''Abstract simple command interpreter.'''
    
    
    extensionName = None
    '''the extension name of this command interpreter, of type `str`.'''
    
    documentFormatNames = None
    '''set of `str` extension names of the document formats supported by this interpreter.'''


    def __init__(self, doc):
        
        '''
        Initializes this interpreter for the specified document.
        
        :Parameters:
            doc : `Document`
                the document for which this interpreter should be initialized.
        '''
        
        super(SimpleCommandInterpreter, self).__init__()
        
        self._docFormat = doc.documentFormat
        self._commands = self._createCommands()
        
        
    def _createCommands(self):
        
        '''
        Creates the commands of this interpreter.
        
        :Returns:
            a mapping from command names to commands.
            
            A command is a callable that accepts zero or more string arguments and
            returns a new `Observation`. A command interpreter typically invokes a
            command with arguments obtained by parsing command text.
        '''
        
        raise NotImplementedError()


    def interpretCommand(self, command):
        
        '''
        Interprets the specified command text to create a new observation.
        
        :Parameters:
            command : `str`
                the command text to be interpreted.
                
        :Returns:
            a new `Observation` created from the command text.
        '''
        
        callable, args = self._parseCommand(command)
        return callable(*args)
    
    
    def _parseCommand(self, command):
        
        try:
            tokens = TokenUtils.tokenizeString(command)
        except ValueError as e:
            raise CommandInterpreterError('Could not parse command. {:s}'.format(str(e)))
        
        if len(tokens) == 0:
            return
        
        return self._getCommandAndArgs(tokens)
        
    
    def _getCommandAndArgs(self, tokens):
        
        try:
            command = self._commands[tokens[0]]
            
        except KeyError:
            # first command token is not a command name
            
            # Try to split digits from end of first token.
            try:
                splitTokens = _splitToken(tokens[0])
            except ValueError:
                _handleUnrecognizedCommandName(tokens[0])
            
            # Try to look up first split token as a command name.
            try:
                command = self._commands[splitTokens[0]]
            except KeyError:
                _handleUnrecognizedCommandName(tokens[0])
            
            tokens = splitTokens + tokens[1:]
            
        return (command, tokens[1:])
    
    
_COMPOUND_TOKEN_RE = re.compile(r'^(\D+)(\d+)$')


def _splitToken(token):
    
    m = _COMPOUND_TOKEN_RE.match(token)
     
    if m is None:
        raise ValueError()
    
    else:
        return list(m.groups())
        
    
def _handleUnrecognizedCommandName(name):
    raise CommandInterpreterError('Unrecognized command "{:s}".'.format(name))
    