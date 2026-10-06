import unittest
from src.calc.cli import execute_operation

class TestCli(unittest.TestCase):
    def test_add(self):
        self.assertEqual(execute_operation("add", 2, 3), 5)
    def test_subtract(self):
        self.assertEqual(execute_operation("subtract", 5, 3), 2)
    def test_multiply(self):
        self.assertEqual(execute_operation("multiply", 4, 5), 20)
    def test_divide(self):
        self.assertEqual(execute_operation("divide", 10, 2), 5)
    def test_divide_by_zero(self):
        with self.assertRaises(ValueError):
            execute_operation("divide", 10, 0)

if __name__ == '__main__':
    unittest.main()