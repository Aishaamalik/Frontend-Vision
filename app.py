import streamlit as st
import base64
from PIL import Image
from backend import extract_text_from_image, generate_code_from_text
import streamlit.components.v1 as components
import zipfile
import io

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

# User customization options
col1, col2 = st.columns(2)
with col1:
    framework = st.selectbox("Framework", ["html", "react"], index=0)
with col2:
    style = st.selectbox("Style", ["minimal", "modern", "material"], index=0)

hint = st.text_input("Optional hint (e.g., 'This is a feedback form')", "")

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

                # Generate code using backend function with options
                content = generate_code_from_text(extracted_text, framework, 'light', style, hint)

                # Parse and display the response in organized sections
                st.subheader("Generated Frontend Code")

                # Split by sections
                sections = content.split('## ')
                html_code = ""
                css_code = ""
                js_code = ""
                detected_components = ""
                analysis = ""
                for section in sections:
                    if section.strip():
                        if section.startswith('Detected Components'):
                            detected_components = '\n'.join(section.split('\n')[1:]).strip()
                            st.markdown(f"### {section.split('\n')[0]}")
                            st.write(detected_components)
                        elif section.startswith('Analysis'):
                            analysis = '\n'.join(section.split('\n')[1:]).strip()
                            st.markdown(f"### {section.split('\n')[0]}")
                            st.write(analysis)
                        elif 'Code' in section:
                            section_title = section.split('\n')[0]
                            st.markdown(f"### {section_title}")
                            # Extract code blocks
                            code_start = section.find('```')
                            if code_start != -1:
                                code_end = section.find('```', code_start + 3)
                                if code_end != -1:
                                    code_block = section[code_start + 3:code_end].strip()
                                    if section_title.lower().startswith('html') or section_title.lower().startswith('react'):
                                        st.code(code_block, language='html' if framework == 'html' else 'javascript')
                                        html_code = code_block
                                    elif section_title.lower().startswith('css'):
                                        st.code(code_block, language='css')
                                        css_code = code_block
                                    elif section_title.lower().startswith('javascript'):
                                        st.code(code_block, language='javascript')
                                        js_code = code_block
                                    else:
                                        st.code(code_block)
                                else:
                                    st.write(section[code_start:].strip())
                            else:
                                st.write(section.split('\n', 1)[1].strip() if '\n' in section else section)

                # Live preview
                if html_code and css_code:
                    full_html = f"""
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Preview</title>
                        <style>{css_code}</style>
                    </head>
                    <body>
                        {html_code}
                        <script>{js_code}</script>
                    </body>
                    </html>
                    """
                    st.subheader("Live Preview")
                    components.html(full_html, height=600, scrolling=True)

                # Download as ZIP
                if html_code or css_code or js_code:
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                        if html_code:
                            zip_file.writestr('index.html', full_html)
                        if css_code:
                            zip_file.writestr('styles.css', css_code)
                        if js_code:
                            zip_file.writestr('script.js', js_code)
                    zip_buffer.seek(0)
                    st.download_button("Download Code as ZIP", data=zip_buffer, file_name="frontend_code.zip")

            except Exception as e:
                st.error(f"Error: {str(e)}")
