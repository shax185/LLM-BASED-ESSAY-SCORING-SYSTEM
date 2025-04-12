import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API Key
API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise ValueError("API key not found. Set GROQ_API_KEY in your environment variables.")

# Initialize LLM (single instance to be reused)
llm = ChatGroq(
    api_key=API_KEY,
    model_name="llama3-70b-8192",
    temperature=0.4
)