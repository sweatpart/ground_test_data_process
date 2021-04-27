from ..pipeline_torque_rainflow import Worker
import unittest

class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.test_worker = Worker()
        self.assertEqual()
    
    def test_method_1(self):
        args = [1]
        result = '1'
        #self.assertEqual(self.test_worker.method(*args), result)

    def test_method_2(self):
        args = [2]
        result = '11'
        #self.assertEqual(self.test_worker.method(*args), result)

    def test_method_3(self):
        args = [3]
        result = '21'
        #self.assertEqual(self.test_worker.method(*args), result)

    def test_method_4(self):
        args = [4]
        result = '1211'
        #self.assertEqual(self.test_worker.method(*args), result)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(MyTestCase('test_method_1'))
    suite.addTest(MyTestCase('test_method_2'))
    suite.addTest(MyTestCase('test_method_3'))
    suite.addTest(MyTestCase('test_method_4'))
    return suite 

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())