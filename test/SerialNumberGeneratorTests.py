from maka.util.SerialNumberGenerator import SerialNumberGenerator

from MakaTests import TestCase

    
class SerialNumberGeneratorTests(TestCase):
    
    
    def testInit(self):
        self._test(SerialNumberGenerator(), 0)
        self._test(SerialNumberGenerator(100), 100)
        
        
    def _test(self, generator, firstNumber):
        for i in range(10):
            self.assertEqual(generator.nextNumber, firstNumber + i)
            
            
    def testSerialNumberGeneration(self):
        
        g = SerialNumberGenerator()
        self._test(g, 0)
            
        g.nextNumber = 0
        self._test(g, 0)

        g.nextNumber = 100        
        self._test(g, 100)
    