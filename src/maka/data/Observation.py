'''
Module containing `Observation` class.

The `Observation` class is the superclass of all observation classes. Its metaclass
processes declarative observation class definitions to create the observation classes
from which observation instances are created. The `Observation` initializer initializes
all fields of a new observation, and allows their values to be set via keyword arguments.
'''


from __future__ import print_function

from maka.data.Field import Field


'''
Documents will use JSON.

Basic idea is to define a Python class for each observation type so we can write code like:

    if obs.isinstance(Fix):
        print(obs.azimuth, obs.declination, obs.objectSype, obs.objectId)

An assignment to a field of an observation should check the assigned value and raise
a ValueError if the value is inappropriate:

    obs.azimuth = 'Hello'           # raises ValueError
    obs.azimuth = -1                # raises ValueRror
    obs.azimuth = 10.4              # fine
    
Do we really need this? Perhaps it would be fine for observations to just be bunches, at
least initially.

We *may* want assignment to a field to trigger:

    value checking
    notification
    
I don't think we must have notification for a simple text editor, though it wouldn't hurt.
I do believe that we will want it when we add the viewer, or more generally to update one
or more views of an observation via the observer pattern.

In any case, we must be able to parse and format field values, and we must be able to
generate an editing UI for an observation, so we must have observation type information
somewhere that tells us what fields an observation has and what their types are. Two
important questions pertaining to this type information are:

1. How do we represent it for configuration purposes?
2. How do we represent it within the program?

The nice thing about a traits-like facility is that it answers both questions at once.

class Float(Field):

    def __init__(minValue=None, maxValue=None, minInclusive=True, maxInclusive=True)
        self._value = ...
        
    def setValue(
        
        
class Azimuth(Float):
    def __init__():
        super(Azimuth, self).__init__(minValue=0, maxValue=360, maxInclusive=False)
        
        
class Fix(Observation):

    azimuth = Azimuth()
    declination = Declination()
    objectType = ObjectType()
    objectId = ObjectId()
    
    
We need to parse and format field values. My inclination would be *not* to include parsing
and formatting in the field classes themselves but rather to keep those functions separate.
This will make it possible to use different sets of parsing and formatting classes in
different situations, e.g. different locales.

    obs.azimuth = parseAzimuth(
An observation always has a type that indicates what its fields are and how to check values
for them. How can we ensure that values are checked on assignment? We could use something like
Enthought traits, though I think I would want to roll my own if possible to keep dependencies
to a minimum. This could make it nicer to write code that manipulates observations. I think
this means that field attributes would be descriptors. And I believe that metaclasses would
be involved in creating observation classes. I don't know the details, but I doubt that it's
terribly complicated. A simple but less convenient alternative would be to require that the
programmer assign a value to a field via a function call, e.g.:

    obs.azimuth.setValue(

How to define observation types?
'''


# My initial inclination was to make the following attribute name start with double
# underscores. However, I found when I tried to create an attribute named `'__fields'`
# in a class named `Fix` that Python (2.7) renamed it to `'_Fix__fields'`.
FIELDS_ATTRIBUTE_NAME = 'FIELDS'


class _Metaclass(type):
    
    '''
    Metaclass of observation types.
    
    The `__new__` method of this class creates observation type classes from the components
    of the class definitions.
    '''
    
    def __new__(cls, typeName, parents, attrs):
        
        fields = _accumulateParentFields(parents)
        fields.update(_getNewFields(attrs))
        
        names = sorted(fields.keys())
        attrs[FIELDS_ATTRIBUTE_NAME] = [fields[name] for name in names]
            
        return type.__new__(cls, typeName, parents, attrs)
        
        
def _accumulateParentFields(parents):
    
    '''
    Accumulates the fields of the specified parent classes in a single dictionary,
    with proper overriding behavior.
    
    :Parameters:
        parents : sequence of `Observation` classes
            the parent classes of the `Observation` class being created, in MRO.
            
    :Returns:
        the accumulated fields of the specified parent classes, in a dictionary
        mapping field names to fields.
        
        The parent fields are accumulated in reverse MRO for proper overriding
        behavior.
    '''
    
    fields = {}
    
    for parent in reversed(parents):
        
        # We can't just say `if issubclass(parent, Observation):` here since when this
        # function is compiled `Observation` is not yet defined.
        if parent.__class__ == _Metaclass:
            parentFields = getattr(parent, FIELDS_ATTRIBUTE_NAME)
            fields.update(dict((f.name, f) for f in parentFields))
        
    return fields


def _getNewFields(attrs):
    
    '''Collects fields from `attrs` and tells them their names.'''
                
    fields = {}
    
    for name, obj in attrs.items():
        
        # TODO: Is it really best to allow field classes as well as instances in
        # observation class definitions? It's a little more concise, but it is also
        # potentially confusing.
        
        try:
            fieldSubclass = issubclass(obj, Field)
        except TypeError:
            fieldSubclass = False
            
        if fieldSubclass:
            obj = obj()
            attrs[name] = obj
            
        if fieldSubclass or isinstance(obj, Field):
            obj._setName(name)
            fields[name] = obj
            
    return fields


class Observation(object, metaclass=_Metaclass):
        
        
    '''Superclass of all observation classes.'''
    
    
    def __init__(self, **kwds):
        
        super(Observation, self).__init__()
        
        self._listeners = None
        
        fields = getattr(self, FIELDS_ATTRIBUTE_NAME)
        
        for field in fields:
            
            try:
                value = kwds[field.name]
            except KeyError:
                value = field.default
            
            field._setValue(self, value)
            
               
    def __eq__(self, obj):
        
        cls = self.__class__
        
        if not isinstance(obj, cls):
            return False
            
        fields = getattr(cls, FIELDS_ATTRIBUTE_NAME)
            
        for field in fields:
                
            name = field.name
                
            if getattr(obj, name) != getattr(self, name):
                return False
                
        # If we get here, all field values were equal.
        return True
        
        
    def __ne__(self, obj):
        return not self.__eq__(obj)
    
            
    def __repr__(self):
        cls = self.__class__
        fields = getattr(cls, FIELDS_ATTRIBUTE_NAME)
        fieldValues = [f.name + '=' + repr(getattr(self, f.name)) for f in fields]
        return cls.__name__ + '(' + ', '.join(fieldValues) + ')'
    
    
    def copy(self, **kwds):
        cls = self.__class__
        fields = getattr(cls, FIELDS_ATTRIBUTE_NAME)
        fieldValues = dict((f.name, getattr(self, f.name)) for f in fields)
        fieldValues.update(kwds)
        return cls(**fieldValues)
    
    
    def notifyFieldValueChanged(self, fieldName, oldValue, newValue):
        pass
#        print('observation field "{:s}" value changed from {:s} to {:s}'.format(
#                  fieldName, str(oldValue), str(newValue)))
