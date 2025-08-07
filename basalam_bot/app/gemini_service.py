"""Integration with Gemini API or its mock for product extraction."""

from dotenv import load_dotenv
load_dotenv()

import os
from typing import List
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Prompt template for extracting product names
EXTRACTION_PROMPT = (
    """
    You are an expert product name extractor. Given a user message, extract all product names mentioned in the text. 
    Return ONLY a Python list of product names (as strings, in the original language), nothing else. 
    Example: ['تونر', 'برش', 'کرم']
    Message: {message}
    """
)

def extract_products(message: str) -> tuple[list[str], str]:
    """Extract product names from message using Google Gemini AI. Returns (product_list, raw_output)."""
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    prompt = EXTRACTION_PROMPT.format(message=message)
    response = model.generate_content(prompt)
    raw_output = response.text.strip()
    # Try to safely evaluate the response as a Python list
    import ast
    try:
        products = ast.literal_eval(raw_output)
        if isinstance(products, list):
            return [str(p).strip().lower() for p in products if isinstance(p, str)], raw_output
    except Exception:
        pass
    return [], raw_output
