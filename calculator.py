"""
Simple Calculator Module
Provides basic arithmetic operations
"""

def add(a, b):
    """Add two numbers and return the result"""
    return a + b

def subtract(a, b):
    """Subtract b from a and return the result"""
    return a - b

def main():
    """Demo the calculator functions"""
    print("Simple Calculator")
    print(f"5 + 3 = {add(5, 3)}")
    print(f"10 - 4 = {subtract(10, 4)}")

if __name__ == "__main__":
    main()
