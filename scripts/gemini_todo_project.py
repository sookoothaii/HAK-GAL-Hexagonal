# Gemini Code Generator - To-Do-Liste
# Erstellt von: Google Gemini AI Agent
# Task-ID: 378ccd2d-26a2-4476-847f-2aa3d3750f9d

tasks = []
completed_tasks = []

def add_task():
    task = input("Geben Sie die Aufgabe ein: ")
    tasks.append(task)
    print("Aufgabe hinzugefügt!")

def display_tasks():
    if not tasks:
        print("Keine Aufgaben vorhanden.")
        return
    print("\nOffene Aufgaben:")
    for i, task in enumerate(tasks):
        print(f"{i+1}. {task}")
    if completed_tasks:
        print("\nErledigte Aufgaben:")
        for i, task in enumerate(completed_tasks):
            print(f"{i+1}. {task}")


def complete_task():
    display_tasks()
    if not tasks:
        return
    try:
        index = int(input("Geben Sie die Nummer der zu erledigenden Aufgabe ein: ")) - 1
        if 0 <= index < len(tasks):
            completed_tasks.append(tasks.pop(index))
            print("Aufgabe erledigt!")
        else:
            print("Ungültige Aufgabennummer.")
    except ValueError:
        print("Ungültige Eingabe.")


def delete_task():
    display_tasks()
    if not tasks:
        return
    try:
        index = int(input("Geben Sie die Nummer der zu löschenden Aufgabe ein: ")) - 1
        if 0 <= index < len(tasks):
            del tasks[index]
            print("Aufgabe gelöscht!")
        else:
            print("Ungültige Aufgabennummer.")
    except ValueError:
        print("Ungültige Eingabe.")


while True:
    print("\nTo-Do-Liste")
    print("1. Aufgabe hinzufügen")
    print("2. Aufgaben anzeigen")
    print("3. Aufgabe erledigen")
    print("4. Aufgabe löschen")
    print("5. Beenden")

    choice = input("Ihre Wahl: ")

    if choice == '1':
        add_task()
    elif choice == '2':
        display_tasks()
    elif choice == '3':
        complete_task()
    elif choice == '4':
        delete_task()
    elif choice == '5':
        break
    else:
        print("Ungültige Wahl.")