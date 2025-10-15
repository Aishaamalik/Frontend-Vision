import streamlit as st
import base64
from PIL import Image
from backend import extract_text_from_image, generate_code_from_text

# Set page config with dark theme to match background
st.set_page_config(
    page_title="Frontend Vision",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def set_bg_with_overlay(img_path, overlay_rgba="rgba(0,0,0,0)"):
    with open(img_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: linear-gradient({overlay_rgba}, {overlay_rgba}), url("data:image/png;base64,{b64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .stApp .css-1d391kg {{ /* container text background tweak (class may vary) */
            background: rgba(255,255,255,0.0);
        }}
        /* Dark theme colors to match background */
        .stTextInput, .stTextArea, .stSelectbox {{
            background-color: rgba(255,255,255,0.1) !important;
            color: white !important;
            border: 1px solid rgba(255,255,255,0.3) !important;
        }}
        .stButton>button {{
            background-color: rgba(255,255,255,0.2) !important;
            color: white !important;
            border: 1px solid rgba(255,255,255,0.5) !important;
        }}
        .stButton>button:hover {{
            background-color: rgba(255,255,255,0.3) !important;
        }}
        .stMarkdown, .stText {{
            color: white !important;
        }}
        .stSubheader {{
            color: #ffffff !important;
        }}
        .stCodeBlock {{
            background-color: rgba(0,0,0,0.5) !important;
            border: 1px solid rgba(255,255,255,0.2) !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_bg_with_overlay("pic1.jpg", overlay_rgba="rgba(0,0,0,0.6)")

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
                extracted_text = extract_text_from_image(image)
                st.subheader("Extracted Text from Image")
                st.text(extracted_text)

                # Generate code using backend function
                content = generate_code_from_text(extracted_text)

                # Parse and display the response in organized sections
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
