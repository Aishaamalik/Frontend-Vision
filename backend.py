import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from PIL import Image
import pytesseract
import re

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
    max_tokens=2000  # Increased for more detailed responses
)

def extract_text_from_image(image):
    """Extract text from image using OCR."""
    return pytesseract.image_to_string(image)

def clean_code(code, language):
    """Clean up generated code: remove redundancies, standardize indentation."""
    if language == 'html':
        # Remove extra <br> tags
        code = re.sub(r'<br\s*/?>\s*<br\s*/?>', '<br>', code)
        # Basic indentation (simple)
        lines = code.split('\n')
        indented = []
        indent_level = 0
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('</'):
                indent_level -= 1
            indented.append('  ' * indent_level + stripped)
            if stripped.startswith('<') and not stripped.startswith('</') and not stripped.endswith('/>'):
                indent_level += 1
        code = '\n'.join(indented)
    elif language == 'css':
        # Standardize indentation
        lines = code.split('\n')
        indented = []
        for line in lines:
            if line.strip():
                indented.append('  ' + line.strip())
            else:
                indented.append('')
        code = '\n'.join(indented)
    elif language == 'javascript':
        # Preserve formatting, just strip leading/trailing whitespace
        code = code.strip()
    return code

def generate_code_from_text(extracted_text, hint=''):
    """Generate frontend code based on extracted text with automatic framework and style detection."""
    framework = 'html'  # default for prompt, will be overridden by LLM detection
    base_prompt = f"""Based on this extracted text from a web frontend image: '{extracted_text}'.

Additional context: {hint}

Please analyze the extracted text to determine the most appropriate frontend framework and style for the web page. Supported frameworks: HTML, React, Vue, Angular, Svelte. Supported styles: minimal, modern, material, bootstrap, tailwind.

First, detect the framework and style, then generate a complete, functional web page accordingly. Structure your response as follows:

## Detected Framework
State the detected framework (e.g., HTML, React, etc.)

## Detected Style
State the detected style (e.g., minimal, modern, etc.)

## Detected Components
List the UI components detected (e.g., - 4 Input Fields, - 1 Button, etc.)

## Analysis
Brief description of the frontend based on the extracted text, including layout understanding.

## Code
```{'html' if framework == 'html' else 'jsx' if framework == 'react' else 'vue' if framework == 'vue' else 'ts' if framework == 'angular' else 'svelte'}
<!-- Complete code here -->
```

## CSS Code
```css
/* Complete CSS code here, using detected style */
```

## JavaScript Code
```javascript
// Complete JavaScript code here
```

Enhancements:
- Optimize for better alignment, spacing, and responsiveness. Match proportions from the image.
- Make the code responsive using flexbox or grid, with max-width and @media queries for mobile and desktop.
- Use modern best practices, rounded corners, soft shadows for the detected style.
- Ensure functional web page.
- For React, generate a functional component with hooks.
- For Vue, use Vue 3 composition API.
- For Angular, use TypeScript.
- For Svelte, use modern Svelte syntax."""

    response = llm.invoke(base_prompt)
    content = response.content

    # Extract detected framework and style from content
    detected_framework = 'html'  # default
    detected_style = 'minimal'  # default
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.strip().startswith('## Detected Framework'):
            detected_framework = lines[i+1].strip().lower() if i+1 < len(lines) else 'html'
        elif line.strip().startswith('## Detected Style'):
            detected_style = lines[i+1].strip().lower() if i+1 < len(lines) else 'minimal'

    # Post-process: Clean the code sections
    sections = content.split('## ')
    cleaned_sections = []
    for section in sections:
        if 'Code' in section and '```' in section:
            code_start = section.find('```')
            code_end = section.find('```', code_start + 3)
            if code_end != -1:
                code_block = section[code_start:code_end + 3]
                lang = 'html' if 'HTML' in section or detected_framework == 'html' else ('javascript' if detected_framework in ['react', 'vue', 'svelte'] else 'typescript' if detected_framework == 'angular' else 'html')
                cleaned_code = clean_code(code_block[3:-3], lang)  # Remove ``` and clean
                section = section[:code_start] + f"```{lang}\n{cleaned_code}\n```" + section[code_end + 3:]
        cleaned_sections.append(section)
    content = '## '.join(cleaned_sections)

    return content, detected_framework, detected_style
