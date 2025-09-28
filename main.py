import ollama
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve the API key from the environment
api_key = os.getenv("OLLAMA_API_KEY")

if not api_key:
    raise ValueError("OLLAMA_API_KEY not found. Make sure it's set in your .env file.")

# Create a custom Ollama client with the Authorization header
client = ollama.Client(
    host='https://ollama.com',
    headers={"Authorization": f"Bearer {api_key}"}
)

# Use the custom client for web_search
try:
    response = client.web_search("What is Ollama?")
    print(response)
except Exception as e:
    print(f"An error occurred: {e}")