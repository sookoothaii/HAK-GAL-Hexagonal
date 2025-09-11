def hello():
    print("Hello World")
    return True

def calculate(x, y):
    return x + y

# Main function
if __name__ == "__main__":
    hello()
    result = calculate(5, 3)
    print(f"Result: {result}")