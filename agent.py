import os
from groq import Groq
from prompts import agent_system
from memory import insert_memories, recall_memories
import json 
from dotenv import load_dotenv
from utils import add_task,list_tasks,complete_task
# from datetime import datetime


load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)
# todoist API token 
API_TOKEN = os.getenv("TODOIST_API_TOKEN")


messages=[
    {
        "role": "system",
        "content": agent_system
    }
    ]

def run_conversation(user_prompt):
    MODEL = "llama3-groq-70b-8192-tool-use-preview" #"llama3-70b-8192"



    messages.append({"role": "user", "content": user_prompt})
    tools = [
    {
        "type": "function",
        "function": {
            "name": "recall_memories",
            "description": "Retrieve relevant memories based on a given query",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "A text query to search and retrieve relevant memories"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "The maximum number of memory results to return (optional, defaults to 3)",
                        "default": 3
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "insert_memories",
            "description": "Insert one or multiple memories into the collection",
            "parameters": {
                "type": "object",
                "properties": {
                    "memories": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "A list of memory contents to be inserted. Can be a single memory or multiple memories."
                    }
                },
                "required": ["memories"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Add a new task to Todoist.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The name or description of the task."
                    },
                    "due_string": {
                        "type": "string",
                        "description": "Due date for the task in natural language, e.g., 'tomorrow'. Optional.",
                        "default": None
                    }
                },
                "required": ["content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List all tasks from Todoist.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a Todoist task as completed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The ID of the task to complete."
                    }
                },
                "required": ["task_id"]
            }
        }
    }
]

    response = client.chat.completions.create(
        model=MODEL, # LLM to use
        messages=messages, # Conversation history
        stream=False,
        tools=tools, # Available tools (i.e. functions) for our LLM to use
        tool_choice="auto", # Let our LLM decide when to use tools
        max_tokens=4096 # Maximum number of tokens to allow in our response
    )
    response_message = response.choices[0].message
    
    tool_calls = response_message.tool_calls
    if tool_calls:
        available_functions = {
            "recall_memories": recall_memories, 
            "insert_memories": insert_memories,
            "add_task": add_task,
            "list_tasks": list_tasks,
            "complete_task": complete_task
        }
        messages.append(response_message)

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            
            if function_name == "recall_memories":
                function_response = function_to_call(
                    query=function_args.get("query"),
                    num_results=function_args.get("num_results", None)
            )
            elif function_name == "insert_memories":
                function_response = function_to_call(
                    memories=function_args.get("memories")
            )
            
            elif function_name == "add_task":
                function_response = function_to_call(
                content=function_args.get("content"),
                due_string=function_args.get("due_string", None)
        )
            elif function_name == "list_tasks":
                raw_response = function_to_call()
                if isinstance(raw_response, list):  # Ensure the response is valid
                    function_response = "\n".join(
                        [f"- {task['content']} (Due: {task['due']['string']})" for task in raw_response if 'due' in task]
                        ) or "No tasks found."
                else:
                    function_response = "Failed to fetch tasks."
            elif function_name == "complete_task":
                function_response = function_to_call(
                task_id=function_args.get("task_id")
        )

        
        # Add the tool response to the conversation
        messages.append(
            {
                "tool_call_id": tool_call.id, 
                "role": "tool", # Indicates this message is from tool use
                "name": function_name,
                "content": str(function_response),
            }
        )
    
    # Make a second API call with the updated conversation
    second_response = client.chat.completions.create(
        model=MODEL,
        messages=messages
    )
    # Return the final response
    final_response = second_response.choices[0].message.content
    messages.append({"role": "assistant", "content": final_response})
    return final_response



while (user_prompt := input("user: ")) != "/exit":
    print(f"Ultron: {run_conversation(user_prompt)}")
