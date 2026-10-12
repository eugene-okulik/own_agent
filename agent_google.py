import time
from datetime import datetime

from google import genai # pip install google-genai
from google.genai import errors

API_KEY = ""  # your token
MODEL = "gemini-3.5-flash-lite"

client = genai.Client(api_key=API_KEY)

context = []

def read_file(path: str) -> str:
    """Read and return the full content of a file."""
    with open(path, encoding="utf-8") as f:
        return f.read()


def write_file(path: str, content: str) -> str:
    """Create or overwrite a file with the given content."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Saved {len(content)} characters to {path}"


chat = client.chats.create(
    model=MODEL,
    config={
        "system_instruction": (
            "You are a coding agent working in the current directory. "
            "Complete the user's task using the read_file and write_file tools. "
            "When finished, briefly report what you did."
        ),
        "tools": [read_file, write_file], # как видите, передаем прям сами функции
    },
)

while True:
    question = input("Your question: ")

    # response = chat.send_message(question) - Вот этой строкой мы и отправляем свой текст и
    # дополняем контекст. Закомментил я его потому что ниже сделаю это в цикле с повторными
    # попытками если гугл будет перегружен и выдаст ошибку 429 или 503. В этом случае мы будем
    # ждать 60 секунд и повторять попытку.

    while True:
        try:
            response = chat.send_message(question)
            break
        except errors.APIError as e:
            if e.code not in (429, 503):
                raise
            # Пишем, что мы наткнулись на ограничение и будем ждать 60 секунд,
            # при этом указываем во сколько начали ждать
            started = datetime.now().strftime("%H:%M:%S")
            print(f"Rate limited / overloaded. Waiting 60s (started {started})...")
            time.sleep(60)
    print(response.text)
