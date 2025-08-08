"""Integration with Gemini API or its mock for product extraction."""

from dotenv import load_dotenv
load_dotenv()

import os
from typing import List
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Prompt template for extracting product names
EXTRACTION_PROMPT = """You are a versatile and intelligent extraction assistant for an e-commerce platform. Analyze Persian user messages with extreme precision and extract accurate product names. Your process must include: 1. Correcting all spelling errors and Farsi-glish. 2. Identifying associated brands and combining them with the product name. 3. Ignoring all extra words and conversational phrases. Your final output should be a pure and precise list of complete product names, ready for a database search.
Return the response in JSON format with the following structure:
{{
    "products": ["product1", "product2"],
    "confidence": 0.95,
    "language": "fa",
    "extracted_count": 2
}}
Message: {message}"""

def extract_products(message: str) -> tuple[list[str], str]:
    """Extract product names from message using Google Gemini AI. Returns (product_list, raw_output)."""
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    prompt = EXTRACTION_PROMPT.format(message=message)
    response = model.generate_content(prompt)
    raw_output = response.text.strip()
    # Try to safely parse the response as JSON
    import json
    try:
        # Clean the raw output by removing Markdown-like formatting
        cleaned_output = raw_output.strip('```json').strip()
        data = json.loads(cleaned_output)
        if isinstance(data, dict) and "products" in data:
            products = data["products"]
            return [str(p).strip() for p in products if isinstance(p, str)], raw_output
    except json.JSONDecodeError as e:
        # Debugging: Log the error if JSON parsing fails
        print(f"JSONDecodeError: {e}")
    return [], raw_output
