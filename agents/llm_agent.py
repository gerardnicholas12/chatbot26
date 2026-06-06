import os
import sys
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq client
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    # Don't exit here - let the app load and fail gracefully when trying to use the LLM
    print("WARNING: GROQ_API_KEY not found in environment", file=sys.stderr)
    client = None
else:
    client = Groq(api_key=api_key)

class LLMAgent:

    def __init__(self):
        self.model = "llama-3.3-70b-versatile"

    def generate(self, user_query, context="", history=None):
        try:
            if not client:
                raise Exception("GROQ_API_KEY environment variable not set. Please check your .env file.")
            
            messages = [
                {
                    "role": "system",
                    "content": """
                    You are ChatBot26.

                    You are a helpful AI assistant.
                    Answer clearly and professionally.
                    Use the provided context if available.
                    If no context is available, answer from general knowledge.
                    """
                }
            ]

            if context:
                messages.append({
                    "role": "system",
                    "content": f"Retrieved Context:\n{context}"
                })

            # Add conversation history if provided
            if history:
                for msg in history[-5:]:  # Keep last 5 messages for context
                    if msg["role"] in ["user", "assistant"]:
                        messages.append(msg)

            messages.append({
                "role": "user",
                "content": user_query
            })

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_completion_tokens=1024
            )

            return response.choices[0].message.content
        except Exception as e:
            error_msg = f"LLM Error: {str(e)}"
            print(error_msg, file=sys.stderr)
            raise


# Singleton instance
llm_agent = LLMAgent()