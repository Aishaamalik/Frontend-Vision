import streamlit as st
import base64
from PIL import Image
from backend import extract_text_from_image, generate_code_from_text
import streamlit.components.v1 as components
import zipfile
import io
from datetime import datetime

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

# Initialize session state for history
if 'history' not in st.session_state:
    st.session_state.history = []

st.title("Frontend Vision")
st.write("Upload an image of a web app frontend, and I'll analyze it to generate code!")

# Sidebar for history
with st.sidebar:
    st.header("History")
    if st.session_state.history:
        for i, entry in enumerate(reversed(st.session_state.history)):
            with st.expander(f"{entry['timestamp']} - {entry['image_name']}"):
                st.write(f"**Framework:** {entry['framework']}")
                st.write(f"**Style:** {entry['style']}")
                st.write(f"**Extracted Text:** {entry['extracted_text'][:100]}...")
                if st.button(f"View Details {i}", key=f"view_{i}"):
                    st.session_state.selected_history = entry
                    st.rerun()
    else:
        st.write("No history yet.")

# Main content
if 'selected_history' in st.session_state:
    entry = st.session_state.selected_history
    st.header("History Details")
    st.write(f"**Timestamp:** {entry['timestamp']}")
    st.write(f"**Image:** {entry['image_name']}")
    st.write(f"**Framework:** {entry['framework']}")
    st.write(f"**Style:** {entry['style']}")
    st.subheader("Extracted Text")
    st.text(entry['extracted_text'])
    st.subheader("Generated Code")
    for section, code in entry['code_sections'].items():
        st.markdown(f"### {section}")
        st.code(code, language='html' if section.lower().startswith('html') or section.lower().startswith('react') else ('css' if section.lower().startswith('css') else 'javascript'))
    if st.button("Back to Main"):
        del st.session_state.selected_history
        st.rerun()
else:
    # No manual selection; framework and style will be detected automatically

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

                # Generate code using backend function with automatic detection
                content, detected_framework, detected_style = generate_code_from_text(extracted_text, "")

                # Display detected framework and style
                st.subheader("Detected Framework and Style")
                st.write(f"**Framework:** {detected_framework.capitalize()}")
                st.write(f"**Style:** {detected_style.capitalize()}")

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
                                    if section_title.lower().startswith('html') or section_title.lower().startswith('react') or section_title.lower().startswith('code'):
                                        st.code(code_block, language='html' if detected_framework == 'html' else 'javascript')
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

                # Store in history
                history_entry = {
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'image_name': uploaded_file.name,
                    'framework': detected_framework,
                    'style': detected_style,
                    'extracted_text': extracted_text,
                    'code_sections': {
                        'Detected Components': detected_components,
                        'Analysis': analysis,
                        f"{detected_framework.upper()} Code": html_code,
                        'CSS Code': css_code,
                        'JavaScript Code': js_code
                    }
                }
                st.session_state.history.append(history_entry)

            except Exception as e:
                st.error(f"Error: {str(e)}")
