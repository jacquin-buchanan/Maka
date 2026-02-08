'''
Module containing class `SerialPort`

Note that this module depends on the PySerial serial communications Python extension.
'''


from __future__ import print_function

from serial import Serial, SerialException, SerialTimeoutException
import serial


# On Mac OS X, a typical USB to serial converter device name is 'cu.usbserial' or
# 'tty.usbserial' and the corresponding device files are '/dev/cu.usbserial' and
# '/dev/tty.usbserial'. On Windows, the converter appears as a COM port: check
# the Device Manager to figure out which one.


class SerialPort(object):
    
    '''
    Serial communication port.
    
    An instance of this class wraps an instance of the `Serial` class of the PySerial
    serial communications Python extension, optionally transforming exceptions raised
    by `Serial` methods into exceptions of another type.
    
    Note that the functionality of this class is quite limited. It does not support
    reading or modifying the port configuration, for example. It is intended only to
    simplify the implementation of certain Maka input device classes, mainly by
    supporting the transformation of exceptions as mentioned above.
    '''
    
    
    def __init__(
        self,
        portName,
        baudRate,
        numDataBits,          # 5, 6, 7, 8
        parity,               # 'None', 'Even', 'Odd', 'Mark', 'Space'
        numStopBits,          # 1, 1.5, 2
        readTimeout=None,
        writeTimeout=None,
        exceptionClass=None):
    
        self._exceptionClass = exceptionClass
        
        # Validate parameters before passing to Serial constructor
        baudRate = _validateBaudRate(baudRate)
        readTimeout = _validateTimeout(readTimeout, 'read')
        writeTimeout = _validateTimeout(writeTimeout, 'write')
        
        byteSize = _getByteSize(numDataBits)
        parity = _getParity(parity)
        stopBits = _getStopBits(numStopBits)
        
        self._serialPort = self._try('initialization', Serial, *[], **{
            'port': None,
            'baudrate': baudRate,
            'bytesize': byteSize,
            'parity': parity,
            'stopbits': stopBits,
            'timeout': readTimeout,
            'writeTimeout': writeTimeout
        })
        
        # We set the port name here rather than above since the latter would open the port.
        # We defer opening the port until we actually want to use it.
        self._try('initialization', self._serialPort.setPort, portName)


    def _try(self, name, callable_, *args, **kwds):
        
        '''
        Invokes a callable that uses the serial port, transforming any resulting
        `SerialException` exceptions into exceptions of type `self._exceptionClass`
        (if the latter is provided).
        '''
        
        if self._exceptionClass is None:
            return callable_(*args, **kwds)
            
        else:

            try:
                return callable_(*args, **kwds)
            
            except SerialException as e:
                raise self._exceptionClass(
                    'Serial port {:s} failed with message: {:s}'.format(name, str(e)))
            
            
    def open(self):
        
        try:
            return self._try('open', self._serialPort.open)
            
        # We catch OSError here because of an apparent bug in the `open` method of
        # pySerial's `PosixSerial` module, which leaks OSError exceptions raised by the
        # Python function `os.open` (Python 2.7.3, Mac OS X).
        except OSError as e:
            raise self._exceptionClass('Serial port open failed with message: {:s}'.format(str(e)))


    def write(self, data):
        try:
            return self._try('write', self._serialPort.write, data)
        except SerialTimeoutException:
            if self._exceptionClass is None:
                raise
            else:
                raise self._exceptionClass('Serial port write timed out.')
        

    def flush(self):
        return self._try('flush', self._serialPort.flush)
        
        
    def flushOutput(self):
        return self._try('output flush', self._serialPort.flushOutput)
    
    
    def flushInput(self):
        return self._try('input flush', self._serialPort.flushInput)
    
    
    def read(self, numBytes):
        return self._try('read', self._serialPort.read, numBytes)
        

    def close(self):
        return self._try('close', self._serialPort.close)


# In the following we specify the possible values of serial communication
# parameters as lists of dictionary items rather than as dictionaries so
# we can specify key order for error messages.


def _processDictItems(items):
    keys = [k for k, _ in items]
    return keys, dict(items)


_BYTE_SIZES_ITEMS = (
    (5, serial.FIVEBITS),
    (6, serial.SIXBITS),
    (7, serial.SEVENBITS),
    (8, serial.EIGHTBITS)
)
_BYTE_SIZES_KEYS, _BYTE_SIZES = _processDictItems(_BYTE_SIZES_ITEMS)


_PARITIES_ITEMS = (
    ('None', serial.PARITY_NONE),
    ('Even', serial.PARITY_EVEN),
    ('Odd', serial.PARITY_ODD),
    ('Mark', serial.PARITY_MARK),
    ('Space', serial.PARITY_SPACE)
)
_PARITIES_KEYS, _PARITIES = _processDictItems(_PARITIES_ITEMS)


_STOP_BITS_ITEMS = (
    (1, serial.STOPBITS_ONE),
    (1.5, serial.STOPBITS_ONE_POINT_FIVE),
    (2, serial.STOPBITS_TWO)
)
_STOP_BITS_KEYS, _STOP_BITS = _processDictItems(_STOP_BITS_ITEMS)


def _getByteSize(numDataBits):
    
    try:
        return _BYTE_SIZES[numDataBits]
    
    except KeyError:
        raise ValueError(
            'Unrecognized number of serial communication data bits. '
            'Number must be ' + _formatList(_BYTE_SIZES_KEYS) + '.')
    
    
def _formatList(items):
    
    reprs = [repr(item) for item in items]
    
    n = len(reprs)
    
    if n == 1:
        return reprs[0]
    
    elif n == 2:
        return reprs[0] + ' or ' + reprs[1]
    
    else:
        return ''.join(r + ', ' for r in reprs[:-1]) + 'or ' + reprs[-1]
    
    
def _getParity(parity):
    
    try:
        return _PARITIES[parity]
    
    except KeyError:
        raise ValueError(
            'Unrecognized serial communication parity. '
            'Parity must be ' + _formatList(_PARITIES_KEYS) + '.')
    
    
def _getStopBits(numStopBits):
    
    try:
        return _STOP_BITS[numStopBits]
    
    except KeyError:
        raise ValueError(
            'Unrecognized number of serial communication stop bits. '
            'Number must be ' + _formatList(_STOP_BITS_KEYS) + '.')


def _validateBaudRate(baudRate):
    '''Validates and returns the baud rate.'''
    
    if not isinstance(baudRate, int):
        try:
            baudRate = int(baudRate)
        except (ValueError, TypeError):
            raise ValueError(
                'invalid literal for int() with base 10: {!r}'.format(baudRate))
    
    if baudRate <= 0:
        raise ValueError(
            'Not a valid baudrate: {:d}'.format(baudRate))
    
    return baudRate


def _validateTimeout(timeout, timeoutType):
    '''Validates and returns a timeout value (read or write).'''
    
    if timeout is None:
        return None
    
    if not isinstance(timeout, (int, float)):
        try:
            timeout = float(timeout)
        except (ValueError, TypeError):
            raise ValueError(
                'Not a valid timeout: {!r}'.format(timeout))
    
    if timeout < 0:
        raise ValueError(
            'Not a valid timeout: {:g}'.format(timeout))
    
    return timeout
