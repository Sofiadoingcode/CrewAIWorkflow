import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from calc.ops import add, subtract, multiply, divide  # noqa: E402

def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("error: wrong number of arguments")
        return 2

    operation = argv[0]
    try:
        a = float(argv[1])
        b = float(argv[2])
    except ValueError:
        print("error: not a number")
        return 2

    if operation == "add":
        result = add(a, b)
        print(result)
        return 0
    elif operation == "subtract":
        result = subtract(a, b)
        print(result)
        return 0
    elif operation == "multiply":
        result = multiply(a, b)
        print(result)
        return 0
    elif operation == "divide":
        try:
            result = divide(a, b)
            print(result)
            return 0
        except ValueError as e:
            print(f"error: {e}")
            return 1
    else:
        print("error: unknown operation")
        return 2

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))