import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.1-8b-instant",   
    temperature=0.7,
    max_tokens=200
)

response = llm.invoke("Write a short poem about coding in Python.")
print(response.content)