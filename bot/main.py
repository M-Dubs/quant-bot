import os
from dotenv import load_dotenv

load_dotenv()

print("Quant Bot Starting...")

api_key = os.getenv("API_KEY")
mode = os.getenv("MODE", "demo")

print(f"Running in {mode} mode with key: {api_key[:4]}***")
