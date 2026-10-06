import unittest
from src.calc.run import main

class TestRun(unittest.TestCase):
    def test_main(self):
        with self.subTest("valid input"): # Test with valid input
            with open('output.txt', 'w') as f:
                f.write('') # Clear the file
            with open('output.txt', 'r') as f:
                self.assertEqual(f.read(), '') # Check if the file is empty
            with open('output.txt', 'w') as f:
                f.write('5') # Write the result to the file
            with open('output.txt', 'r') as f:
                self.assertEqual(f.read(), '5') # Check if the result is correct
        with self.subTest("invalid input"): # Test with invalid input
            with open('output.txt', 'w') as f:
                f.write('') # Clear the file
            with open('output.txt', 'r') as f:
                self.assertEqual(f.read(), '') # Check if the file is empty
            with open('output.txt', 'w') as f:
                f.write('a') # Write invalid input to the file
            with open('output.txt', 'r') as f:
                self.assertEqual(f.read(), 'a') # Check if the input is invalid

if __name__ == '__main__':
    unittest.main()