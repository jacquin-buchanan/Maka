from __future__ import print_function

from collections import defaultdict
import calendar
import datetime
import re

from maka.format.DocumentFormat import DocumentFormat
from maka.format.FieldFormat import FieldFormat
from maka.format.ObservationFormat import ObservationFormat
from maka.util.TokenUtils import NONE_TOKEN as FORMATTED_NONE
import maka.util.TokenUtils as TokenUtils


# TODO: Support more format customization, e.g. for dates, times, and angles.


_EDITING_NONE = ''
'''The formatted-for-editing value of an observation field value of `None`.'''


_QUOTABLE_CHARS_RE = re.compile(r'[\s\\"]')


class StringFormat(FieldFormat):
    
    '''
    String field value format.
    
    We format and parse string values differently depending on context. Normally
    when we format a string value we escape backslashes and quotes and add
    surrounding quotes. In a context in which a string is to be edited, however,
    we format it without escapes or surrounding quotes. In either context, of course,
    we parse a formatted string value according to how it was formatted.
    '''
    
    def __init__(self):
        super(StringFormat, self).__init__('string')
        
        
    def format(self, v, editing=False):
        
        if editing:
            return _EDITING_NONE if v is None else v

        elif v is None:
            return FORMATTED_NONE
        
        elif len(v) == 0:
            return '""'
        
        elif _QUOTABLE_CHARS_RE.search(v) is None:
            
            # When a string contains no whitespace, backslashes, or quotes, we format it
            # without surrounding quotes.
            return v
        
        else:
            return '"' + _escapeString(v) + '"'
    
    
    def parse(self, s, editing=False):
        
        if editing:
            return None if s == _EDITING_NONE else s
            
        elif s == FORMATTED_NONE:
            return None
        
        elif s[0] == '"':
            # quoted string
            
            # We do not check the string contents here, assuming that happened during tokenization.
            return _unescapeString(s[1:-1])
        
        else:
            # unquoted string
            
            return s
    
    
def _escapeString(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')


def _unescapeString(s):
    return s.replace('\\\\', '\\').replace('\\"', '"')


# TODO: Eliminate redundancy with expression in `Field` module.
_DECIMAL_RE = re.compile(r'^-?(\d+\.?|\d*\.\d+)$')


class DecimalFormat(FieldFormat):
    
    
    def __init__(self):
        super(DecimalFormat, self).__init__('decimal')
        
        
    def format(self, v, editing=False):
        
        if v is None:
            return _EDITING_NONE if editing else FORMATTED_NONE
        
        else:
            return v
        
        
    def parse(self, s, editing=False):
        
        if editing and s == _EDITING_NONE or not editing and s == FORMATTED_NONE:
            return None
        
        else:

            m = _DECIMAL_RE.match(s)
            
            if m is None:
                raise ValueError('Bad decimal number "{:s}".'.format(s))
                
            else:
                return s


class IntegerFormat(FieldFormat):
    
    
    def __init__(self, replacementField='{:d}'):
        
        super(IntegerFormat, self).__init__('integer')
        
        try:
            replacementField.format(0)
        except Exception:
            raise ValueError('Bad integer replacement field "{:s}".'.format(replacementField))
        
        self.replacementField = replacementField
        
        
    def format(self, v, editing=False):
        
        if v is None:
            return _EDITING_NONE if editing else FORMATTED_NONE
        
        else:
            return self.replacementField.format(v)
    
    
    def parse(self, s, editing=False):
        
        if editing and s == _EDITING_NONE or not editing and s == FORMATTED_NONE:
            return None
        
        else:
            try:
                return int(s)
            except ValueError:
                raise ValueError('Could not parse "{:s}" as an integer.'.format(s))
        
        
class FloatFormat(FieldFormat):
    
    
    def __init__(self, replacementField='{:.16g}'):
        
        super(FloatFormat, self).__init__('float')
        
        try:
            replacementField.format(0)
        except Exception:
            raise ValueError('Bad integer replacement field "{:s}".'.format(replacementField))
        
        self.replacementField = replacementField
        
        
    def format(self, v, editing=False):
        if v is None:
            return _EDITING_NONE if editing else FORMATTED_NONE
        else:
            return self.replacementField.format(v)
    
    
    def parse(self, s, editing=False):
        
        if editing and s == _EDITING_NONE or not editing and s == FORMATTED_NONE:
            return None
        
        else:
            try:
                return float(s)
            except ValueError:
                raise ValueError('Could not parse "{:s}" as a floating point number.'.format(s))
        
        
_ANGLE_RE = re.compile(r'^(-?)(\d{1,3}):(\d\d):(\d\d)$')


class AngleFormat(FieldFormat):
    
    
    def __init__(self):
        super(AngleFormat, self).__init__('ddd:mm:ss')
        
        
    def format(self, v, editing=False):
        
        if v is None:
            return _EDITING_NONE if editing else FORMATTED_NONE
        
        else:
            
            if v < 0:
                sign = '-'
                v = -v
            else:
                sign = ''
                
            totalSeconds = int(round(3600 * v))
            seconds = totalSeconds % 60
            
            totalMinutes = totalSeconds // 60
            minutes = totalMinutes % 60
            
            degrees = totalMinutes // 60
            
            return '{:s}{:d}:{:02d}:{:02d}'.format(sign, degrees, minutes, seconds)
        
        
    def parse(self, s, editing=False):
        
        if editing and s == _EDITING_NONE or not editing and s == FORMATTED_NONE:
            return None
        
        else:
            
            m = _ANGLE_RE.match(s)
            
            if m is None:
                raise ValueError('Bad angle "{:s}".'.format(s))
                
            else:
                (sign, degrees, minutes, seconds) = m.groups()
                v = float(degrees) + float(minutes) / 60. + float(seconds) / 3600.
                if sign == '-':
                    v = -v
                return v
            
        
_DATE_RE = re.compile(r'^(\d{1,2})/(\d{1,2})/(\d{2})$')


class DateFormat(FieldFormat):
    
    
    def __init__(self):
        super(DateFormat, self).__init__('dd/mm/ss')
        
        
    def format(self, v, editing=False):
        if v is None:
            return _EDITING_NONE if editing else FORMATTED_NONE
        else:
            return '{:d}/{:d}/{:02d}'.format(v.month, v.day, v.year % 100)
        
        
    def parse(self, s, editing=False):
        
        if editing and s == _EDITING_NONE or not editing and s == FORMATTED_NONE:
            return None
        
        else:
            
            m = _DATE_RE.match(s)
            
            if m is None:
                raise ValueError('Bad date "{:s}".'.format(s))
                
            else:
                
                (month, day, year) = m.groups()
                
                month = int(month)
                day = int(day)
                year = int(year)
                
                year += (2000 if year < 70 else 1900)
                
                if month == 0 or month > 12:
                    raise ValueError('Month must be in range [1, 12].')
                
                (_, numDays) = calendar.monthrange(year, month)
                
                if day == 0 or day > numDays:
                    raise ValueError('For {:s}, {:d} day must be in range [1, {:d}].'.format(
                                         calendar.month_name[month], year, numDays))
                
                return datetime.date(year, month, day)
            
        
_TIME_RE = re.compile(r'^(\d{1,2}):(\d\d):(\d\d)$')


class TimeFormat(FieldFormat):
    
    
    def __init__(self):
        super(TimeFormat, self).__init__('hh:mm:ss')
        
        
    def format(self, v, editing=False):
        if v is None:
            return _EDITING_NONE if editing else FORMATTED_NONE
        else:
            return '{:d}:{:02d}:{:02d}'.format(v.hour, v.minute, v.second)
        
        
    def parse(self, s, editing=False):
        
        if editing and s == _EDITING_NONE or not editing and s == FORMATTED_NONE:
            return None
        
        else:
            
            m = _TIME_RE.match(s)
            
            if m is None:
                raise ValueError('Bad time "{:s}".'.format(s))
                
            else:
                
                (hour, minute, second) = m.groups()
                
                hour = int(hour)
                minute = int(minute)
                second = int(second)
                
                if hour > 23:
                    raise ValueError('Hour must be in range [0, 23].')
                
                if minute > 59:
                    raise ValueError('Minute must be in range [0, 59].')
                
                if second > 59:
                    raise ValueError('Second must be in range [0, 59].')
                
                return datetime.time(hour, minute, second)
            
        
class Literal(object):
    
    '''
    A literal may be *key*, in which case it is unique to its observation. No other
    observation includes the same literal, so the literal can be used to classify
    an observation as being of a particular type.
    '''
    
    
    def __init__(self, text):
        
        super(Literal, self).__init__()
        
        if text.endswith('*'):
            self.text = text[:-1]
            self.isKey = True
        else:
            self.text = text
            self.isKey = False
        
        
    def format(self):
        return self.text
    
    
    def parse(self, s):
        if s != self.text:
            raise ValueError('Bad literal "%s": expecting "%s".'.format(s, self.text))
        
        
class SimpleObservationFormat(ObservationFormat):
    
    
    def __init__(self, formatString, obsClass, fieldFormats):
        
        super(SimpleObservationFormat, self).__init__(obsClass)
        
        self._items, self._keyIndex = _parseObsFormatString(
            formatString, obsClass, fieldFormats)
        
        self._fieldOrder = tuple(name for name, _ in self._items if name != '')
        
        self._fieldFormats = dict((name, format) for name, format in self._items if name != '')
        
        
    @property
    def items(self):
        return self._items
    
    
    @property
    def keyIndex(self):
        return self._keyIndex
    
    
    def formatObservation(self, obs):
        return ' '.join(_applyObsFormatItem(i, obs) for i in self._items)
    
    
    def parseObservation(self, s):
        return self._parseTokens(TokenUtils.tokenizeString(s), s)
        
        
    def _parseTokens(self, tokens, s):
        
        items = self._items
        
        if len(tokens) != len(items):
            raise ValueError(
                ('Observation "{:s}" of type "{:s}" has wrong number of tokens '
                 '({:d} instead of {:d}).').format(
                    s, self.observationClass.__name__, len(tokens), len(items)))
            
        parsedTokens = [self._parseToken(tokens[i], item, name)
                         for i, (name, item) in enumerate(items)]
        
        fields = dict((name, value) for (name, value) in parsedTokens if name != '')
        
        return self.observationClass(**fields)
    
    
    def _parseToken(self, token, item, name):
        try:
            return (name, item.parse(token))
        except ValueError as e:
            raise ValueError('For observation field "{:s}": {:s}'.format(name, str(e)))
    
    
    def getFieldFormat(self, fieldName):
        return self._fieldFormats[fieldName]
    
    
'''
An *observation format string* is a sequence of space-separated *items*. Each item is either
a *field format string* or a *literal*. A field format string is of the form *{<field name>}*,
where *<field name>* is the name of an observation field. A literal begins with a non-"{"
character but otherwise may contain any non-whitespace characters.

To format an observation, a string is derived from each item of the format string and these
strings are joined with spaces. For each field format string, the appropriate field format
class is used to format the named observation field, and each literal is included as is.
'''


def _parseObsFormatString(formatString, obsClass, fieldFormats):
    
    items = []
    for item in formatString.split():
        try:
            items.append(_parseObsFormatItem(item, obsClass, fieldFormats))
        except ValueError as e:
            raise ValueError(
                'Error parsing item "{:s}" of observation format "{:s}": {:s}'.format(
                    item, formatString, str(e)))
    
    keyIndices = [
        i for i, (_, item) in enumerate(items) if isinstance(item, Literal) and item.isKey]
    
    if len(keyIndices) == 0:
        raise ValueError('No key specified in observation format "{:s}".'.format(formatString))
    
    return tuple(items), keyIndices[0]
        

def _parseObsFormatItem(item, obsClass, fieldFormats):
    
    if item.startswith('{'):
        # item is a field format string
        
        if item.endswith('}'):
            
            parts = item[1:-1].split(':', 1)
            fieldName = parts[0]
            args = [] if len(parts) == 1 else ['{:' + parts[1] + '}']
                
            field = _getObsField(obsClass, fieldName, item)
            formatClass = _getFormatClass(field.__class__, fieldFormats)
                
            return (fieldName, formatClass(*args))
        
        else:
            # format string starts with "{" but doesn't end with "}"
            
            _handleBadFieldFormatString(item, 'String must start with "{" and end with "}".')
            
    else:
        return ('', Literal(item))
    
    
def _getObsField(obsClass, fieldName, formatString):
    
    try:
        return getattr(obsClass, fieldName)
    
    except AttributeError:
        _handleBadFieldFormatString(
            formatString,
            'Observation type "{:s}" has no field "{:s}".'.format(obsClass.__name__, fieldName))
                
                
def _handleBadFieldFormatString(formatString, message=None):
    message = '' if message is None else ' ' + message
    raise ValueError('Bad field format string "{:s}".{:s}'.format(formatString, message))
    
    
def _getFormatClass(fieldClass, fieldFormats):
    
    try:
        return fieldFormats[fieldClass.__name__]
        
    except KeyError:
        # no field format class for field class name
        
        # Look for field format class for field class superclasses in MRO order.
        for cls in fieldClass.__mro__[1:]:
            try:
                return fieldFormats[cls.__name__]
            except KeyError:
                pass
            
        # If we get here, no field format class is available for either the
        # field class or any of its superclasses.
        raise ValueError(
            'No format class found for field type "{:s}".'.format(fieldClass.__name__))
        
        
def _applyObsFormatItem(item, obs):
    
    (name, item) = item
    
    if name == '':
        return item.format()
    else:
        return item.format(getattr(obs, name))
                    
            
class SimpleDocumentFormat(DocumentFormat):
    
    
    # These must be provided by a subclass.
    observationFormats = None
    fieldFormats = None
    
    
    def __init__(self):
        
        super(SimpleDocumentFormat, self).__init__()
        
        obsClasses = dict((c.__name__, c) for c in self.documentClass.observationClasses)
        
        # Create map from observation class names to observation formats.
        self._obsFormatsByName = dict(
            (className,
             _createObsFormat(className, obsClasses, formatString, self.fieldFormats))
            for className, formatString in self.observationFormats.items())
        
        # Create list of (keyIndex, keys) pairs and map from keys to observation formats.
        keySets = defaultdict(set)
        obsFormats = {}
        for f in self._obsFormatsByName.values():
            key = f._items[f._keyIndex][1].text
            keySets[f._keyIndex].add(key)
            obsFormats[key] = f
        self._keySets = [(keyIndex, frozenset(keys)) for keyIndex, keys in keySets.items()]
        self._keySets.sort(key=lambda x: len(x[1]), reverse=False)
        self._obsFormatsByKey = obsFormats
        
        
    def formatDocument(self, obsSeq):
        return ''.join([self.formatObservation(obs) + '\n' for obs in obsSeq])
    
    
    def parseDocument(self, lines, startLineNum=0):
        
        observations = []
        lineNum = startLineNum
        
        for line in lines:
            
            if len(line) > 0:
                
                try:
                    observations.append(self._parseObs(line))
                except ValueError as e:
                    e.lineNum = lineNum + 1
                    raise
                
            lineNum += 1
            
        return observations
    
    
    def _parseObs(self, s):
        
        tokens = TokenUtils.tokenizeString(s)
        n = len(tokens)
        
        for i, key_set in self._keySets:
            
            # In the following, we assume that if a token matches a key, the token
            # is a literal.
            
            if i < n and tokens[i] in key_set:
                obsFormat = self._obsFormatsByKey[tokens[i]]
                return obsFormat._parseTokens(tokens, s)
            
        # If we get here, no key token was found.
        raise ValueError('Observation type could not be determined.')


    def getObservationFormat(self, obsClassName):
        try:
            return self._obsFormatsByName[obsClassName]
        except KeyError:
            raise ValueError(
                'Could not find format for observation type "{:s}".'.format(obsClassName))
        

def _createObsFormat(obsClassName, obsClasses, formatString, fieldFormats):
    
    try:
        obsClass = obsClasses[obsClassName]
    except KeyError:
        raise ValueError('Could not find observation class "{:s}".'.format(obsClassName))
        
    return SimpleObservationFormat(formatString, obsClass, fieldFormats)
    

'''
How we will implement the grammar features of Maka:

I would like to separate observation types from UI, including forms and commands.

* Observation types are Python classes, created with the aid of a special metaclass.
  An observation type specifies a list of fields.

* Field types are Python descriptor classes, and fields are descriptor instances.

* A *field format* knows how to format a value of a particular field type as
  a string, and how to parse a formatted string into a value. A field format
  optionally specifies a *format hint*, some text that can be displayed in a
  UI to guide text entry.
  
* A *form* displays an observation in a GUI for editing. It is constructed from
  an observation type and a set of field formats.

* A *command interpreter* constructs observations from terse keyboard *commands*.
  Command interpreters are not specified declaratively, but rather are Python
  objects with certain methods and state. (But could they be specified
  declaratively? That is what Aardvark offered, and such an approach has advantages,
  basically simplicity. Perhaps command interpreters could be created either
  declaratively or imperatively?)

* Forms and command interpreters heed *translation sets* associated with observation
  fields. A translation set has a name and a map from untranslated strings to
  translated strings. Translation sets are associated with observation type fields
  via a map from observation type fields (specified as (<observation type name>,
  <field name>) pairs) to translation set names.
  
It might be a good idea to allow specification of Maka configuration data in some
text format such as JSON that is independent of any particular programming language.
Unfortunately I have found that JSON specification is more cumbersome than Python
specification. It might still be a good idea, however, so that various Maka-
related tools can be implemented in various programming languages.

It might also be a good idea to support inspection and editing of Maka
configuration data via a GUI, for users who are not programmers.

In summary, a Maka configuration comprises:

Field and observation types:
1. Field types
2. Observation types

Field and observation formats:
3. Field formats
4. Observation formats

Observation text entry support:
5. Translation sets
6. Association of translation sets with observation type fields

Command interpreter for entering observations:
7. Command interpreter

Forms for editing observations:
8. Forms, one for each observation type, mostly or entirely automatically generated.
'''


'''
Station 1 "Old Ruins" Lat 20 4.925283850520 Lon -155 51.794984516976 El 65.6 MagDec 10:16:00 
Theodolite 1 "Sokkia DT500 S/N 13303" AzOffset 0:00:00 DecOffset 0:00:00 
Reference 1 "White Marker" Azimuth 315:20:30 
Observer asf "Adam Frankel" 
00000 1/01/12 00:00:00 Comment 0 "White marker is 315:20:30" 
'''
