'''Observation field classes.'''


from __future__ import print_function

import datetime
import re


_FIELD_VALUE_NAME_PREFIX = '_'


class Field(object):
    
    '''
    Superclass of all observation field classes.
    
    This class and its subclasses are Python *descriptor* classes that customize read
    and write access to the observation attributes that store observation field values.
    The customizations perform type and range checking of assigned values, and notify
    listeners of value changes. The workings of Python descriptor classes and instances
    are documented in the "Data Model" section of the "Python Language Reference".
    '''
    
    
    TYPE_NAME = None
    '''
    `None` or a short, uncapitalized string describing the type of values of this field,
    for example `'string'`, `'integer'`, `'decimal'`, or `'date'`.
    '''
    
    UNITS = None
    '''
    `None` or string describing field value units, for example `'meters'` or
    `'degrees below zenith'`.
    '''
    
    RANGE = None
    '''
    `None` or string describing field value range, for example `'[0, 5]'` or
    `'{"R", "G", "B"}'`.
    '''
    
    DOC = None
    '''field documentation string.'''
    
    DEFAULT = None
    '''the default field value.'''
    
    _valueClasses = None
    '''field value classes, to one of which the value of the field (if not `None`) must belong.'''
    
    
    def __init__(self, **kwds):
        
        super(Field, self).__init__()
        
        # Unlike for other properties below, we do not support the specification of a
        # default field name as a field class attribute since a field name is always
        # specified as a class attribute of the owning observation type.
        self._name = kwds.get('name', None)
        
        self._typeName = kwds.get('typeName', self.TYPE_NAME)
        self._units = kwds.get('units', self.UNITS)
        self._range = kwds.get('range', self.RANGE)
        self._doc = kwds.get('doc', self.DOC)
        
        default = kwds.get('default', self.DEFAULT)
        self._typeCheck(default)
        self._default = default
        
        
    @property
    def name(self):
        return self._name
    
    
    def _setName(self, name):
        self._name = name
        self._valueName = _FIELD_VALUE_NAME_PREFIX + name
        
        
    @property
    def typeName(self):
        return self._typeName
    
    
    @property
    def units(self):
        return self._units
    
    
    @property
    def range(self):
        return self._range
    
    
    # TODO: Do we really need this?
    @property
    def doc(self):
        return self._doc
    
    
    @property
    def default(self):
        return self._default
    
    
    def __get__(self, obs, obs_class):
        return getattr(obs, self._valueName) if obs is not None else self
    
    
    def __set__(self, obs, value):
        
        '''
        Set the value of this field on the specified observation with notification.
        
        The value is set if and only if the new value differs from the old one.
        '''
        
        oldValue = getattr(obs, self._valueName)
        
        if value != oldValue:
            self._setValue(obs, value)
            obs.notifyFieldValueChanged(self.name, oldValue, value)
        
        
    def _setValue(self, obs, value):
        
        '''
        Set the value of this field on the specified observation without notification.
        
        The value is set regardless of whether it differs from the old one, or whether
        there is an old value at all.
        '''
        
        if value is not None:
            self._check(value)
        setattr(obs, self._valueName, value)
        
        
    def _check(self, value):
        
        '''
        Check whether `value` is a valid value for this field.
        
        :Parameters:
            value : `object`
                the value to check.
                
        :Raises TypeError:
            if and only if `value` is of the wrong type for this field.
            
        :Raises ValueError:
            if and only if `value` is of the correct type but is not a valid value for this field.
        '''
        
        self._typeCheck(value)
        self._rangeCheck(value)
        
        
    def _typeCheck(self, value):
        
        if value is not None and self._valueClasses is not None:
            
            for c in self._valueClasses:
                if isinstance(value, c):
                    return
            
            # If we get here, the value is not of a recognized type.
            self._raiseTypeCheckError(value)
            
            
    def _raiseTypeCheckError(self, value):
                
        classes = self._valueClasses
        
        numClasses = len(classes)
        
        if numClasses == 0:
            s = 'None'
            
        elif numClasses == 1:
            s = '{:s} or None'.format(classes[0].__name__)
            
        else:
            s = ', '.join(['{:s}'.format(c.__name__) for c in classes]) + ', or None'
            
        raise TypeError(
            '{:s} field value must be {:s}, but found {:s}.'.format(
                _className(self), s, _className(value)))
        
        
    def _rangeCheck(self, value):
        pass


class String(Field):
    
    
    TYPE_NAME = 'string'
    VALUES = None
    RANGE = None
    TRANSLATIONS = None
    
    
    _valueClasses = (str,)
    
    
    def __init__(self, **kwds):
        
        super(String, self).__init__(**kwds)
        
        self._initValues(kwds.get('values', self.VALUES))
            
        self._range = kwds.get('range', self.RANGE)
        
        self._rangeCheck(self.default, 'default')
        
        self._initTranslations(kwds.get('translations', self.TRANSLATIONS))
                
        
    def _initValues(self, values):
        
        if values is not None:
            
            for value in values:
                self._typeCheck(value)
                
            self._values = tuple(values)
            self._valuesSet = frozenset(values)
            
        else:
            self._values = None
            self._valuesSet = None
            
            
    def _initTranslations(self, translations):
        
        if translations is not None:
            for value in translations.values():
                self._rangeCheck(value, 'translation')
                
        self._translations = translations
        
        
    @property
    def values(self):
        return self._values
    
    
    @property
    def range(self):
        
        if self._range is not None:
            return self._range
        
        elif self.values is not None:
            return '{' + ', '.join('"{:s}"'.format(v) for v in self.values) + '}'
        
        else:
            return None
        
        
    def _rangeCheck(self, value, description=None):
        
        if description is None:
            description = ''
        else:
            description += ' '
            
        if value is not None and self._values is not None and value not in self._valuesSet:
            raise ValueError(
                'Bad {:s} field {:s}value {:s}. Value must be in the set {:s}.'.format(
                    _className(self), description, _quote(value), _formatStringSet(self._values)))
        
        
    def __set__(self, obs, value):
        
        '''
        Set the value of this field on the specified observation with notification.
        
        The value is translated if translations have been specified for this field, and
        the value is set if and only if the new value differs from the old one.
        '''
        
        if self._translations is not None:
            value = self._translations.get(value, value)
            
        oldValue = getattr(obs, self._valueName)
        
        if value != oldValue:
            self._setValue(obs, value, False)
            obs.notifyFieldValueChanged(self.name, oldValue, value)
        

    def _setValue(self, obs, value, translate=True):
        
        '''
        Set the value of this field on the specified observation without notification.
        
        The value is translated if and only if the `translate` argument is `True` and
        translations have been specified for this field.
        
        The value is set regardless of whether it differs from the old one, or whether
        there is an old value at all.
        '''
        
        if translate and self._translations is not None:
            value = self._translations.get(value, value)
            
        if value is not None:
            self._check(value)
            
        setattr(obs, self._valueName, value)
        
        
class Integer(Field):
    
    
    TYPE_NAME = 'integer'
    MIN = None
    MAX = None
    
    _valueClasses = (int,)
    
    
    def __init__(self, **kwds):
        
        super(Integer, self).__init__(**kwds)
        
        min = kwds.get('min', self.MIN)
        self._typeCheck(min)
        self._min = min
            
        max = kwds.get('max', self.MAX)
        self._typeCheck(max)
        self._max = max
        
        if self._range is None:
            self._range = _createRangeString(self.min, True, self.max, True, lambda i: str(i))
            
        self._rangeCheck(self.default)
        
        
    @property
    def min(self):
        return self._min
    
    
    @property
    def max(self):
        return self._max
    
    
    def _rangeCheck(self, value):
        
        if value is None:
            return
            
        if self._min is not None and value < self._min:
            raise ValueError(
                '{:s} field value {:d} is less than minimum allowed value of {:d}.'.format(
                    _className(self), value, self._min))
        
        if self._max is not None and value > self._max:
            raise ValueError(
                '{:s} field value {:d} is greater than maximum allowed value of {:d}.'.format(
                    _className(self), value, self._max))
                    
        
class Float(Field):
    
    
    TYPE_NAME = 'float'
    MIN = None
    MAX = None
    MIN_INCLUSIVE = True
    MAX_INCLUSIVE = True

    
    _valueClasses = (float, int)
    
    
    def __init__(self, **kwds):
        
        super(Float, self).__init__(**kwds)
        
        min = kwds.get('min', self.MIN)
        self._minInclusive = kwds.get('minInclusive', self.MIN_INCLUSIVE)
        self._typeCheck(min)
        self._min = _float(min)
            
        max = kwds.get('max', self.MAX)
        self._maxInclusive = kwds.get('maxInclusive', self.MAX_INCLUSIVE)
        self._typeCheck(max)
        self._max = _float(max)
        
        if self._range is None:
            self._range = _createRangeString(
                self.min, self.minInclusive, self.max, self.maxInclusive, _formatFloat)
            
        self._rangeCheck(self.default)
        
        
    @property
    def min(self):
        return self._min
    
    
    @property
    def minInclusive(self):
        return self._minInclusive
    
    
    @property
    def max(self):
        return self._max
    
    
    @property
    def maxInclusive(self):
        return self._maxInclusive
    
    
    def _setValue(self, obs, value):
        if value is not None:
            self._check(value)
        setattr(obs, self._valueName, _float(value))
        
        
    def _rangeCheck(self, value):
        
        if value is None:
            return
        
        if self._min is not None:
            
            if self._minInclusive:
                if value < self._min:
                    raise ValueError(
                        ('{:s} field value {:s} is less than minimum allowed value of '
                         '{:s}.').format(
                            _className(self),
                            _formatFloat(value),
                            _formatFloat(self._min)))
                    
            elif value <= self._min:
                raise ValueError(
                    ('{:s} field value {:s} is not greater than lower bound of '
                     '{:s}.').format(
                        _className(self), _formatFloat(value), _formatFloat(self._min)))
        
        if self._max is not None:
            
            if self._maxInclusive:
                if value > self._max:
                    raise ValueError(
                        ('{:s} field value {:s} is greater than maximum allowed value of '
                         '{:s}.').format(
                            _className(self),
                            _formatFloat(value),
                            _formatFloat(self._max)))
                    
            elif value >= self._max:
                raise ValueError(
                    '{:s} field value {:s} is not less than upper bound of {:s}.'.format(
                        _className(self), _formatFloat(value), _formatFloat(self._max)))
        
    
# TODO: Eliminate redundancy with expression in `SimpleDocumentFormat` module?
_DECIMAL_RE = re.compile(r'^-?(\d+\.?|\d*\.\d+)$')


class Decimal(Field):
    
    '''
    Decimal number field.
    
    The values of a `Decimal` field are decimal number strings. The same range checking
    is provided as for `Float` fields, except that the minimum and maximum values are
    specified as decimal number strings rather than float literals.
    '''
    
    
    TYPE_NAME = 'decimal'
    MIN = None
    MAX = None
    MIN_INCLUSIVE = True
    MAX_INCLUSIVE = True

    
    _valueClasses = (str,)
    
    
    def __init__(self, **kwds):
        
        super(Decimal, self).__init__(**kwds)
        
        min = kwds.get('min', self.MIN)
        self._minInclusive = kwds.get('minInclusive', self.MIN_INCLUSIVE)
        self._typeCheck(min)
        self._min = min
        self._minFloat = _float(min)

        max = kwds.get('max', self.MAX)
        self._maxInclusive = kwds.get('maxInclusive', self.MAX_INCLUSIVE)
        self._typeCheck(max)
        self._max = max
        self._maxFloat = _float(max)
        
        if self._range is None:
            self._range = _createRangeString(
                self.min, self.minInclusive, self.max, self.maxInclusive, lambda s: s)
            
        self._rangeCheck(self.default)
        self._defaultFloat = _float(self.default)
        
        
    @property
    def min(self):
        return self._min
    
    
    @property
    def minInclusive(self):
        return self._minInclusive
    
    
    @property
    def max(self):
        return self._max
    
    
    @property
    def maxInclusive(self):
        return self._maxInclusive
    
    
    def _setValue(self, obs, value):
        if value is not None:
            self._check(value)
        setattr(obs, self._valueName, value)
        
        
    def _typeCheck(self, value):
        
        super(Decimal, self)._typeCheck(value)
        
        if value is not None and _DECIMAL_RE.match(value) is None:
            raise TypeError(
                '{:s} field value must be decimal number string.'.format(_className(self)))
        
        
    def _rangeCheck(self, value):
        
        if value is None:
            return
        
        valueFloat = _float(value)
        
        if self._minFloat is not None:
            
            if self._minInclusive:
                if valueFloat < self._minFloat:
                    raise ValueError(
                        ('{:s} field value {:s} is less than minimum allowed value of '
                         '{:s}.').format(_className(self), value, self._min))
                    
            elif valueFloat <= self._minFloat:
                raise ValueError(
                    ('{:s} field value {:s} is not greater than lower bound of '
                     '{:s}.').format(_className(self), value, self._min))
        
        if self._maxFloat is not None:
            
            if self._maxInclusive:
                if valueFloat > self._maxFloat:
                    raise ValueError(
                        ('{:s} field value {:s} is greater than maximum allowed value of '
                         '{:s}.').format(_className(self), value, self._max))
                    
            elif valueFloat >= self._maxFloat:
                raise ValueError(
                    '{:s} field value {:s} is not less than upper bound of {:s}.'.format(
                        _className(self), value, self._max))
        
    
class Date(Field):
    TYPE_NAME = 'date'
    _valueClasses = (datetime.date,)


class Time(Field):
    TYPE_NAME = 'time'
    _valueClasses = (datetime.time,)


def _createRangeString(min, minInclusive, max, maxInclusive, formatter):
    
    if min is None and max is None:
        return None
    
    elif min is not None and max is not None:
        left = '[' if minInclusive else '('
        right = ']' if maxInclusive else ')'
        return 'in ' + left + formatter(min) + ', ' + formatter(max) + right
    
    elif min is not None:
        condition = 'greater than or equal to ' if minInclusive else 'greater than '
        return condition + formatter(min)
    
    else:
        condition = 'less than or equal to ' if maxInclusive else 'less than '
        return condition + formatter(max)


def _className(obj):
    return obj.__class__.__name__


_REPLACEMENTS = {
    '\\': '\\\\',    # replace backslash with double backslash
    '"': '\\"'       # replace double quote with backslash and double quote
}
    
    
def _quote(s):
    return '"' + ''.join([_REPLACEMENTS.get(c, c) for c in s]) + '"'


def _formatStringSet(s):
    return '{' + ', '.join([_quote(e) for e in s]) + '}'

    
def _float(x):
    return float(x) if x is not None else None


def _formatFloat(x):
    return '{:.10g}'.format(x)
