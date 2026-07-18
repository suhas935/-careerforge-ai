from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def ask_claude(prompt: str, system: str = "", max_tokens: int = 1500) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content
