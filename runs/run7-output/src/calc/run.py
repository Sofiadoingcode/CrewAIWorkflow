import sys
from src.calc.cli import execute_operation

def main(argv):
    if len(argv) != 3:
        print("Usage: python run.py <operation> <num1> <num2>")
        sys.exit(1)

    operation, num1, num2 = argv
    result = execute_operation(operation, num1, num2)
    print(f"Result: {result}")
    sys.exit(0)