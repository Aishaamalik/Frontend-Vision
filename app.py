import streamlit as st
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from PIL import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Load environment variables
load_dotenv()

# Get API key
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
if not GROQ_API_KEY:
    st.error("GROQ_API_KEY not found in .env file. Please set it.")
    st.stop()

# Initialize the LLM
llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.1-8b-instant",
    temperature=0.7,
    max_tokens=1000
)

st.title("Frontend Vision")
st.write("Upload an image of a web app frontend, and I'll analyze it to generate code!")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image', use_column_width=True)

    if st.button("Analyze and Generate Code"):
        with st.spinner("Analyzing image and generating code..."):
            try:
                # Extract text from image using OCR
                extracted_text = pytesseract.image_to_string(image)
                st.subheader("Extracted Text from Image")
                st.text(extracted_text)

                # Use LLM to analyze the extracted text and generate code
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

                # Parse and display the response in organized sections
                content = response.content
                st.subheader("Generated Frontend Code")

                # Split by sections
                sections = content.split('## ')
                for section in sections:
                    if section.strip():
                        if section.startswith('Analysis'):
                            st.markdown(f"### {section.split('\n')[0]}")
                            st.write('\n'.join(section.split('\n')[1:]).strip())
                        elif 'Code' in section:
                            section_title = section.split('\n')[0]
                            st.markdown(f"### {section_title}")
                            # Extract code blocks
                            code_start = section.find('```')
                            if code_start != -1:
                                code_end = section.find('```', code_start + 3)
                                if code_end != -1:
                                    code_block = section[code_start:code_end + 3]
                                    if section_title.lower().startswith('html'):
                                        st.code(code_block, language='html')
                                    elif section_title.lower().startswith('css'):
                                        st.code(code_block, language='css')
                                    elif section_title.lower().startswith('javascript'):
                                        st.code(code_block, language='javascript')
                                    else:
                                        st.code(code_block)
                                else:
                                    st.write(section[code_start:].strip())
                            else:
                                st.write(section.split('\n', 1)[1].strip() if '\n' in section else section)
            except Exception as e:
                st.error(f"Error: {str(e)}")
