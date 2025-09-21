import math

class Calculator:
    def __init__(self):
        self.history = []

    def add(self, a, b):
        result = a + b
        self.log(f"{a} + {b} = {result}")
        return result

    def subtract(self, a, b):
        result = a - b
        self.log(f"{a} - {b} = {result}")
        return result

    def multiply(self, a, b):
        result = a * b
        self.log(f"{a} * {b} = {result}")
        return result

    def divide(self, a, b):
        if b == 0:
            print("Division durch Null ist nicht erlaubt!")
            return None
        result = a / b
        self.log(f"{a} / {b} = {result}")
        return result

    def power(self, a, b):
        result = a ** b
        self.log(f"{a} ^ {b} = {result}")
        return result

    def sqrt(self, a):
        if a < 0:
            print("Wurzelziehen aus negativen Zahlen ist nicht erlaubt!")
            return None
        result = math.sqrt(a)
        self.log(f"sqrt({a}) = {result}")
        return result

    def log(self, operation):
        self.history.append(operation)

    def show_history(self):
        print("\nLetzte Berechnungen:")
        for i in range(min(5, len(self.history))):
            print(self.history[-1 - i])

    def clear_history(self):
        self.history = []
        print("Historie gelöscht.")

    def average_results(self):
        try:
            results = [float(op[op.index('=') + 2:]) for op in self.history]
            avg = sum(results) / len(results)
            print(f"Der Durchschnitt aller Ergebnisse: {avg}")
        except ZeroDivisionError:
            print("Keine Berechnungen vorhanden, um den Durchschnitt zu berechnen.")

    def find_max_min(self):
        try:
            results = [float(op[op.index('=') + 2:]) for op in self.history]
            max_result = max(results)
            min_result = min(results)
            print(f"Maximum: {max_result}, Minimum: {min_result}")
        except ZeroDivisionError:
            print("Keine Berechnungen vorhanden, um das Maximum und Minimum zu berechnen.")

    def export_history(self):
        with open('history.txt', 'w') as file:
            for entry in self.history:
                file.write(entry + '\n')
        print("Historie wurde erfolgreich exportiert.")


def main():
    calc = Calculator()
    while True:
        print("\n--- Taschenrechner ---")
        print("1. Addition")
        print("2. Subtraktion")
        print("3. Multiplikation")
        print("4. Division")
        print("5. Potenzierung (a^b)")
        print("6. Wurzelziehen (sqrt)")
        print("7. Historie anzeigen")
        print("8. Historie löschen")
        print("9. Durchschnitt aller Ergebnisse berechnen")
        print("10. Maximum und Minimum in der Historie finden")
        print("11. Historie exportieren")
        print("12. Beenden")

        choice = input("Wählen Sie eine Option (1-12): ")

        if choice == '1':
            a = float(input("Erste Zahl: "))
            b = float(input("Zweite Zahl: "))
            calc.add(a, b)
        elif choice == '2':
            a = float(input("Erste Zahl: "))
            b = float(input("Zweite Zahl: "))
            calc.subtract(a, b)
        elif choice == '3':
            a = float(input("Erste Zahl: "))
            b = float(input("Zweite Zahl: "))
            calc.multiply(a, b)
        elif choice == '4':
            a = float(input("Erste Zahl: "))
            b = float(input("Zweite Zahl: "))
            calc.divide(a, b)
        elif choice == '5':
            a = float(input("Basis (a): "))
            b = float(input("Exponent (b): "))
            calc.power(a, b)
        elif choice == '6':
            a = float(input("Zahl: "))
            calc.sqrt(a)
        elif choice == '7':
            calc.show_history()
        elif choice == '8':
            calc.clear_history()
        elif choice == '9':
            calc.average_results()
        elif choice == '10':
            calc.find_max_min()
        elif choice == '11':
            calc.export_history()
        elif choice == '12':
            print("Programm beendet.")
            break
        else:
            print("Ungültige Eingabe. Bitte wählen Sie eine gültige Option (1-12).")

if __name__ == "__main__":
    main()
