import os
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
try:
    models = client.models.list()
    print("Available Models Found!")
    for m in list(models)[:5]:
        print(f" - {m.id}")
except Exception as e:
    print(f"FAILURE: {type(e).__name__} - {str(e)}")
