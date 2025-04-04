# backend/llm_chat.py

import os
import tiktoken
import litellm
from dotenv import load_dotenv
import google.generativeai as genai
from openai import OpenAI
import anthropic

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

litellm.api_key = OPENAI_API_KEY
deepseek_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

MODEL_PRICES = {
    "gpt-4o": 0.15 / 1_000_000,
    "gemini flash free": 0.0,
    "deepseek": 0.07 / 1_000_000,
    "claude-3.5 haiku": 0.80 / 1_000_000
}

def count_tokens(text: str, model: str) -> int:
    try:
        if "gemini" in model.lower() or "claude" in model.lower():
            return len(text.split())
        elif "deepseek" in model.lower():
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        else:
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))
    except Exception as e:
        print(f"Token count error: {e}")
        return 0

def build_prompt(pdf_data: dict, question: str) -> str:
    return f"""
You are a helpful assistant. Use the following document content to answer the question.

Document Content:
{pdf_data.get("pdf_content", "No document content available.")}

User Question:
{question}

Answer the question based solely on the document above.
"""

def get_llm_response(pdf_data: dict, question: str, llm_choice: str) -> dict:
    prompt_text = build_prompt(pdf_data, question)
    model_key = llm_choice.lower()
    token_count = count_tokens(prompt_text, model=model_key)
    cost_per_token = MODEL_PRICES.get(model_key, 0)
    estimated_cost = token_count * cost_per_token

    try:
        if model_key == "gpt-4o":
            response = litellm.completion(
                model="gpt-4o-mini-2024-07-18",
                messages=[{"role": "user", "content": prompt_text}]
            )
            answer = response["choices"][0]["message"]["content"]

        elif model_key == "gemini flash free":
            genai.configure(api_key=GOOGLE_API_KEY)
            model_gemini = genai.GenerativeModel('gemini-1.5-pro-latest')
            response = model_gemini.generate_content(prompt_text)
            answer = response.text

        elif model_key in ["deepseek", "deepseek chat"]:
            response = deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant"},
                    {"role": "user", "content": prompt_text},
                ],
                stream=False
            )
            answer = response.choices[0].message.content

        elif model_key in ["claude", "claude-3", "claude-3.5 haiku"]:
            client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
            response = client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt_text}]
            )
            answer = response.content[0].text if isinstance(response.content, list) else response.content

        else:
            answer = "LLM choice not recognized."

        return {
            "answer": answer,
            "tokens": token_count,
            "cost": estimated_cost
        }

    except Exception as e:
        print(f"Error processing LLM request: {e}")
        return {
            "answer": f"Error: {e}",
            "tokens": token_count,
            "cost": estimated_cost
        }
