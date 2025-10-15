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
                prompt = f"Based on this extracted text from a web frontend image: '{extracted_text}'. Analyze the layout, components, and generate HTML, CSS, and JavaScript code to recreate a similar frontend. Provide the code in a structured format."
                response = llm.invoke(prompt)
                st.subheader("Generated Code")
                st.code(response.content, language='html')
            except Exception as e:
                st.error(f"Error: {str(e)}")
