from __future__ import print_function

import sys

from maka.device.SerialPort import SerialPort


_PORT_NAME = '/dev/cu.usbserial'
_BAUD_RATES = [1200, 2400, 4800, 9600]
_NUM_DATA_BITS = [8, 7]
_PARITIES = ['None', 'Even', 'Odd']
_NUM_STOP_BITS = [1, 2]

_WRITE_STRING = '\x00'
_READ_SIZE = 16


class ReadSucceeded(Exception):
    pass


def _main():
    
    numConfigs = len(_BAUD_RATES) * len(_NUM_DATA_BITS) * len(_PARITIES) * len(_NUM_STOP_BITS)
    configNum = 1
    
    for baudRate in _BAUD_RATES:
        for numDataBits in _NUM_DATA_BITS:
            for parity in _PARITIES:
                for numStopBits in _NUM_STOP_BITS:
                    
                    print('Trying {:d} {:d} {:s} {:g} (configuration {:d} of {:d})...'.format(
                              baudRate, numDataBits, parity, numStopBits, configNum, numConfigs))
    
                    try:
                        _testConfig(baudRate, numDataBits, parity, numStopBits)
                    
                    except ReadSucceeded as e:
                        print('Read yielded "{:s}".'.format(str(e)))
                        sys.exit()
                        
                    except Exception as e:
                        print('Got {:s} with message: {:s}', e.__class__.__name__, str(e))
                        pass
                    
                    configNum += 1
                    
                    
def _testConfig(baudRate, numDataBits, parity, numStopBits):
    
    port = SerialPort(
        _PORT_NAME, baudRate, numDataBits, parity, numStopBits, readTimeout=3, writeTimeout=3)
    
    port.open()
    
    try:
        port.write(_WRITE_STRING)
        result = port.read(_READ_SIZE)
    finally:
        port.close()

    if len(result) != 0:
        raise ReadSucceeded(result)
        
        
if __name__ == '__main__':
    _main()
