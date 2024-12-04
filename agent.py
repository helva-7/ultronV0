import os
from groq import Groq
from prompts import agent_system
from memory import insert_memories, recall_memories
import json 
from dotenv import load_dotenv
# from datetime import datetime


load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

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
            "insert_memories": insert_memories
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
