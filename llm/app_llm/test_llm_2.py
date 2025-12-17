#gemini_demo.py
import os
import time
import google.generativeai as genai

from dotenv import load_dotenv
# Load API key
load_dotenv()
api_key = "AIzaSyDXjnUJ3ep5Dws1YyemQ5HyBdV7OAm7zlI"

if not api_key:
    raise ValueError("❌ Please set GEMINI_API_KEY in your .env file")

genai.configure(api_key=api_key)

#for m in genai.list_models():
#    print(m.name)

model = genai.GenerativeModel("models/gemini-2.5-flash-lite")

# Example prompt
prompt = """
You are a helpful assistant. Be brief and precise.
Calculate 47 * 128, explain the logic, and give only the final result clearly.
"""
print("🧠 Sending prompt to Gemini...")
start = time.time()

response = model.generate_content(prompt)
elapsed = time.time() - start
print("\n✨ Gemini Response:")
print(response.text.strip())
print(f"\n⏱ Time taken: {elapsed:.2f} seconds")