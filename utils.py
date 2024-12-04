import os
from todoist_api_python.api import TodoistAPI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_TOKEN = os.getenv("TODOIST_API_TOKEN")

# Initialize the Todoist API client
api = TodoistAPI(API_TOKEN)

def add_task(content, due_string=None, priority=1):
    """Add a new task to Todoist."""
    try:
        task = api.add_task(content=content, due_string=due_string, priority=priority)
        return f"Task '{task.content}' added with ID: {task.id}"
    except Exception as e:
        return f"Error adding task: {e}"

def list_tasks():
    """List all active tasks."""
    try:
        tasks = api.get_tasks()
        return [f"{task.id}: {task.content}" for task in tasks]
    except Exception as e:
        return f"Error listing tasks: {e}"

def complete_task(task_id):
    """Mark a task as complete."""
    try:
        api.close_task(task_id)
        return f"Task with ID {task_id} marked as complete."
    except Exception as e:
        return f"Error completing task: {e}"
