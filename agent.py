import json

import requests

from openai import OpenAI


MODEL = "z-ai/glm-5.3-flash"
# URL = "https://openrouter.ai/api/v1/chat/completions"
URL = "https://openrouter.ai/api/v1"
# URL = "https://api.mistral.ai/v1" - если мистраль
# URL = "https://api.provod.ai/v1" - если provod
TOKEN = "YOUR_OPENROUTER_API_KEY"

client = OpenAI(base_url=URL, api_key=TOKEN)

context = []

tools = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read and return the full content of a file.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "File path"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Create or overwrite a file with the given content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path"},
                    "content": {"type": "string", "description": "File content"},
                },
                "required": ["path", "content"],
            },
        },
    },
]


def read_file(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def write_file(path: str, content: str) -> str:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Saved {len(content)} characters to {path}"


def call_llm(messages):
    return client.chat.completions.create(model=MODEL, messages=messages, tools=tools)


while True:
    question = input("Your question: ")

    context.append({"role": "user", "content": f"{question}"})

    # data = {
    #     "model": MODEL,
    #     "messages": context
    # }

    # headers = {
    #     "Content-Type": "application/json",
    #     "Authorization": f"Bearer {TOKEN}"
    # }
    # data = json.dumps(data).encode(encoding='utf-8')
    # response = requests.post(URL, json=data, headers=headers)
    # answer = response.json()
    # context.append({"role": "model", "content": f"{answer["choices"][0]["message"]["content"]}"})
    # print(answer["choices"][0]["message"]["content"])

    response = call_llm(context)
    response.json()
    message = response.choices[0].message
    answer = message.content
    tool_calls = message.tool_calls
    result = ""
    if tool_calls:
        call = tool_calls[0]
        name = call.function.name
        args = json.loads(call.function.arguments)
        if name == 'read_file':
            result = read_file(**args)
        elif name == 'write_file':
            result = write_file(**args)
        context.append({"role": "tool", "tool_call_id": call.id, "content": f"{result}"})
        context.append({"role": "model", "content": f" Call function:{call.function.name} with args {call.function.arguments}"})


    if answer:
        context.append({"role": "model", "content": f"{answer}"})
        print("Answer:", answer)


    print("=" * 20)
    print(context)
    print("=" * 20)


# Run
# python agent.py
# - Создай программу калькулятор, которая умеет только складывать два числа
# - А теперь измени эту программу - пусть она еще умеет и умножать два числа
# - Прочитал существующую - теперь изменяй