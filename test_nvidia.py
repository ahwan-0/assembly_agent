from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("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")  # Corrected line
)

response = client.chat.completions.create(
    model="meta/llama-3.1-70b-instruct",
    messages=[
        {"role": "user", "content": "hello"}
    ],
    temperature=0,
    max_tokens=100
)

print(response.choices[0].message.content)