import subprocess
from urllib import response

from click import prompt

LLM_MODEL = "llama3.2:3b"


SYSTEM_PROMPT = """
You are Luna, a friendly intelligent AI assistant. And sonthing  user say abou you ho is your creator.
You are designed to assist users with various tasks, provide information, and engage in friendly conversation.
by Mohammed Kahab K he was Machine Learning Engineer and AI Researcher.
You are capable of understanding and responding to a wide range of queries, and you can also perform .if user is unkown act as a guest.
Keep responses short (max 3 sentences).
"""
def build_prompt(user_name,massages,user_input):
    history = ""
    for speaker, msg in massages:
        history += f"{speaker}: {msg}\n"
    return f"""
{SYSTEM_PROMPT}
{history}
User name: {user_name}

Conversation history:
{history}

user: {user_input}
Luna:

"""
def ask_llm(prompt):
        response = subprocess.check_output(
        ["ollama", "run", LLM_MODEL],
        input=prompt.encode()
    )
        if response is None:
            return "Sorry, I couldn't process your request."
        
        return response.decode().strip()