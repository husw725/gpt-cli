import os
from openai import OpenAI
import sys

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print(f"Testing connection with model: {sys.argv[1]}")
try:
    response = client.chat.completions.create(
        model=sys.argv[1],
        messages=[{"role": "user", "content": "ping"}],
        max_tokens=10
    )
    print("SUCCESS: Connection and authentication are working.")
    print(f"Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"FAILURE: {type(e).__name__} - {str(e)}")
