import requests
import json
import ast
import os
import re
from tools import Tool


class Agent:
    def __init__(self):
        self.tools = []
        self.memory = []
        self.max_memory = 10

    def add_tool(self, tool: Tool):
        self.tools.append(tool)

    def extract_curly_braces_content(self, input_string):
        match = re.search(r"\{.*?\}", input_string)
        if match:
            return match.group()
        return None

    def json_parser(self, input_string):
        result = self.extract_curly_braces_content(input_string)
        python_dict = ast.literal_eval(result)
        json_string = json.dumps(python_dict)
        json_dict = json.loads(json_string)

        if isinstance(json_dict, dict):
            return json_dict

        raise "Invalid JSON response"

    def process_input(self, user_input):
        self.memory.append(f"User: {user_input}")
        self.memory = self.memory[-self.max_memory:]

        context = "\n".join(self.memory)
        tool_descriptions = "\n".join(
            [f"- {tool.name()}: {tool.description()}" for tool in self.tools])
        response_format = {"action": "", "args": ""}

        prompt = f"""Context:
        {context}

        Available tools:
        {tool_descriptions}

        Based on the user's input and context, decide if you should use a tool or respond directly.
        Sometimes you might have to use multiple tools to solve user's input. You have to do that in a loop.
        If you identify a action, respond with the tool name and the arguments for the tool.
        If you decide to respond directly to the user then make the action "respond_to_user" with args as your response in the following format.

        Response Format:
        {response_format}

        """

        response = self.query_llm(prompt)
        self.memory.append(f"Agent: {response}")

        response_dict = self.json_parser(response)

        # Check if any tool can handle the input
        for tool in self.tools:
            if tool.name().lower() == response_dict["action"].lower():
                return tool.use(response_dict["args"])

        return response_dict

    def query_llm(self, prompt):
        os.environ['GROQ_API_KEY'] = "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"
        api_key = os.environ['GROQ_API_KEY']

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        url = "https://api.groq.com/openai/v1/chat/completions"

        data = {
            "messages": [{"role": "user", "content": prompt}],
            "model": "llama-3.3-70b-versatile",
            "temperature": 1,
            "max_completion_tokens": 1024,
            "top_p": 1,
            "stream": False,
            "stop": None
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))
        final_response = response.json(
        )['choices'][0]['message']['content'].strip()
        print("LLM Response ", final_response)
        return final_response

    def run(self):
        print("LLM Agent: Hello! How can I assist you today?")
        user_input = input("You: ")

        while True:
            if user_input.lower() in ["exit", "bye", "close"]:
                print("See you later!")
                break

            response = self.process_input(user_input)
            if isinstance(response, dict) and response["action"] == "respond_to_user":
                print("Reponse from Agent: ", response["args"])
                user_input = input("You: ")
            else:
                user_input = response
