ToDolist=[]
while True:
    command = input("Enter a command (add/remove/view/exit): ").strip().lower()
    if command == "add":
        task = input("Enter the task to add: ").strip()
        ToDolist.append(task)
        print(f"Task '{task}' added to the list.")
    elif command == "remove":
        task = input("Enter the task to remove: ").strip()
        if task in ToDolist:
            ToDolist.remove(task)
            print(f"Task '{task}' removed from the list.")
    elif command == "view":
        print("To-Do List:")
        for i, task in enumerate(ToDolist, start=1):
            print(f"{i}. {task}")
    elif command == "exit":
        print("Exiting the To-Do List program.")
        break
    else:
        print("Invalid command. Please try again.")