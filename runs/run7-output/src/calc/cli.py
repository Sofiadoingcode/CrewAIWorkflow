import sys
from src.calc.ops import add, subtract, multiply, divide

def execute_operation(operation, num1, num2):
    if operation == "add":
        return add(num1, num2)
    elif operation == "subtract":
        return subtract(num1, num2)
    elif operation == "multiply":
        return multiply(num1, num2)
    elif operation == "divide":
        return divide(num1, num2)
    else:
        raise ValueError("Unsupported operation")