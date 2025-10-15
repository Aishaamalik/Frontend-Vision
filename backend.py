import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from PIL import Image
import pytesseract

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Load environment variables
load_dotenv()

# Get API key
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file. Please set it.")

# Initialize the LLM
llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.1-8b-instant",
    temperature=0.7,
    max_tokens=1000
)

def extract_text_from_image(image):
    """Extract text from image using OCR."""
    return pytesseract.image_to_string(image)

def generate_code_from_text(extracted_text):
    """Generate frontend code based on extracted text."""
    prompt = f"""Based on this extracted text from a web frontend image: '{extracted_text}'.

Please analyze what you see and generate a complete, functional web page. Structure your response as follows:

## Analysis
Brief description of the frontend based on the extracted text.

## HTML Code
```html
<!-- Complete HTML code here -->
```

## CSS Code
```css
/* Complete CSS code here */
```

## JavaScript Code
```javascript
// Complete JavaScript code here
```

Make sure the code is well-structured, uses modern best practices, and creates a functional web page."""
    response = llm.invoke(prompt)
    return response.content
