from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the scope for Google Tasks API
SCOPES = ['https://www.googleapis.com/auth/tasks']

def authenticate():
    """
    Authenticate the user and get credentials for accessing Google Tasks API.
    """
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    return creds

def list_tasklists(service):
    """
    List all task lists for the authenticated user.
    """
    tasklists = service.tasklists().list().execute()
    print("Task Lists:")
    for tasklist in tasklists.get('items', []):
        print(f"- {tasklist['title']} (ID: {tasklist['id']})")

def create_tasklist(service, title):
    """
    Create a new task list.
    """
    tasklist = {"title": title}
    service.tasklists().insert(body=tasklist).execute()
    print(f"Task list '{title}' created successfully.")

def delete_tasklist(service, tasklist_id):
    """
    Delete a task list by its ID.
    """
    service.tasklists().delete(tasklist=tasklist_id).execute()
    print(f"Task list with ID '{tasklist_id}' deleted successfully.")

def list_tasks(service, tasklist_id):
    """
    List all tasks in a specific task list.
    """
    tasks = service.tasks().list(tasklist=tasklist_id).execute()
    print(f"Tasks in Task List {tasklist_id}:")
    for task in tasks.get('items', []):
        print(f"- {task['title']} (Status: {task['status']})")

def create_task(service, tasklist_id, title, notes=None):
    """
    Create a new task in a specific task list.
    """
    task = {"title": title, "notes": notes}
    service.tasks().insert(tasklist=tasklist_id, body=task).execute()
    print(f"Task '{title}' created successfully in Task List {tasklist_id}.")

def delete_task(service, tasklist_id, task_id):
    """
    Delete a specific task from a task list.
    """
    service.tasks().delete(tasklist=tasklist_id, task=task_id).execute()
    print(f"Task with ID '{task_id}' deleted successfully.")

if __name__ == "__main__":
    print("Authenticating...")
    credentials = authenticate()
    service = build('tasks', 'v1', credentials=credentials)

    print("\nAvailable options:")
    print("1. List Task Lists")
    print("2. Create Task List")
    print("3. Delete Task List")
    print("4. List Tasks in a Task List")
    print("5. Create Task in a Task List")
    print("6. Delete Task in a Task List")
    print("0. Exit")

    while True:
        choice = input("\nEnter your choice: ")

        match choice:
            case "0":
                print("Exiting...")
                break
            case "1":
                list_tasklists(service)
            case "2":
                title = input("Enter title for new task list: ")
                create_tasklist(service, title)
            case "3":
                tasklist_id = input("Enter Task List ID to delete: ")
                delete_tasklist(service, tasklist_id)
            case "4":
                tasklist_id = input("Enter Task List ID to list tasks: ")
                list_tasks(service, tasklist_id)
            case "5":
                tasklist_id = input("Enter Task List ID to create task in: ")
                title = input("Enter task title: ")
                notes = input("Enter task notes (optional): ")
                create_task(service, tasklist_id, title, notes)
            case "6":
                tasklist_id = input("Enter Task List ID: ")
                task_id = input("Enter Task ID to delete: ")
                delete_task(service, tasklist_id, task_id)
            case _:
                print("Invalid choice. Please try again.")
