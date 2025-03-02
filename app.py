from dotenv import load_dotenv 
import base64
import io
import os
import streamlit as st
from PIL import Image
import pdf2image
import google.generativeai as genai

# ---------- CONFIGURATIONS ----------
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# ---------- CUSTOM THEME & STYLING ----------
def set_custom_theme():
    st.markdown("""
    <style>
    /* Base styling */
    body, .stApp {
        color: #ffffff;
        background-color: #000000;
    }
    
    /* Background pattern */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            linear-gradient(to right, rgba(79, 79, 79, 0.18) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(128, 128, 128, 0.04) 1px, transparent 1px),
            radial-gradient(circle 400px at 50% 300px, rgba(251, 251, 251, 0.21), #000);
        background-size: 14px 24px;
        z-index: -1;
    }

    /* Sidebar styling using new selector */
    [data-testid="stSidebar"] > div:first-child {
        background-color: #000000 !important;
        border-right: 1px solid #333333;
    }

    /* Text elements */
    .stMarkdown, .stTextArea>label, .stButton>button {
        color: #ffffff !important;
    }
    
    /* Headers */
    .brand-header {
        color: #00FF88 !important;
        font-family: 'Courier New', monospace;
        font-size: 2.8em;
        text-align: center;
        margin-bottom: 20px;
        text-shadow: 0 0 10px #00FF88;
    }
    
    .ninja-subheader {
        color: #00FF88 !important;
        text-align: center;
        margin-bottom: 30px;
    }

    /* Buttons */
    .stButton>button {
        background: #1a1a1a !important;
        border: 2px solid #00FF88 !important;
        transition: all 0.3s !important;
    }

    .stButton>button:hover {
        background: #00FF88 !important;
        color: #000000 !important;
    }

    /* Uploader */
    .stFileUploader>label {
        color: #ffffff !important;
    }
    
    /* Success message */
    .stAlert [data-testid="stMarkdownContainer"] {
        color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------- CORE FUNCTIONS ----------
def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        try:
            images = pdf2image.convert_from_bytes(
                uploaded_file.read(),
                poppler_path=r""  # UPDATE THIS PATH
            )
            first_page = images[0]

            img_byte_arr = io.BytesIO()
            first_page.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()

            return [{
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()
            }]
        except Exception as e:
            st.error(f"🔧 Error processing PDF: {e}")
            raise
    raise FileNotFoundError("No file uploaded")

def get_gemini_response(input_prompt, pdf_content, job_desc):
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    try:
        response = model.generate_content([input_prompt, pdf_content[0], job_desc])
        return response.text
    except Exception as e:
        st.error(f"🤖 AI Error: {e}")
        raise

# ---------- STREAMLIT UI ----------
def main():
    # Set custom theme
    set_custom_theme()

    # Main header
    st.markdown('<h1 class="brand-header">NEURAL NET NINJAS</h1>', unsafe_allow_html=True)
    st.markdown('<h3 class="ninja-subheader">⚔️ AI-Powered Resume Combat Analyzer</h3>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("## 🥷 Ninja Toolkit")
        st.markdown("""
        - ATS Compliance Check
        - Skill Gap Analysis
        - Resume Optimization
        - Interview Prep
        """)
        st.markdown("---")
        st.markdown("**Developer Mode:**")
        st.code("NinjaOS v1.4.2 | Gemini API")

    # Main content
    job_desc = st.text_area("🎯 Enter Job Description:", height=150, key="input")
    uploaded_file = st.file_uploader("📤 Upload Resume (PDF)", type=["pdf"])
    
    if uploaded_file:
        st.success("🗡️ Resume Uploaded - Ready for Analysis!")
    col1, col2 = st.columns(2)
    with col1:
        analyze_btn = st.button("🔍 Analyze Resume")
    with col2:
        improve_btn = st.button("⚡ Improve Resume")
    
    analysis_prompt = """
    You are an elite HR ninja with 20 years experience. Analyze this resume against the job description.
    Follow this structure:
    1. Combat Rating (0-100)
    2. Strengths (3 bullet points)
    3. Weaknesses (3 bullet points)
    4. Missing Skills
    5. Optimization Strategy
    """

    improvement_prompt = """
    You are a resume sensei. Provide specific, actionable improvements:
    1. Keyword Optimization
    2. Formatting Fixes
    3. Achievement Boosts
    4. ATS Compliance
    Format as markdown with emojis.
    """

    # Handle actions
    if analyze_btn or improve_btn:
        if uploaded_file:
            with st.spinner("🧠 Engaging Neural Networks..."):
                try:
                    pdf_content = input_pdf_setup(uploaded_file)
                    prompt = analysis_prompt if analyze_btn else improvement_prompt
                    response = get_gemini_response(prompt, pdf_content, job_desc)
                    
                    st.subheader("🗡️ Ninja Analysis")
                    st.markdown(response)
                    
                    # Download button
                    st.download_button(
                        label="💾 Download Report",
                        data=response,
                        file_name="ninja_analysis.md",
                        mime="text/markdown"
                    )
                except Exception as e:
                    st.error(f"🔥 Mission Failed: {e}")
        else:
            st.warning("⚠️ Please upload a resume first!")

if __name__ == "__main__":
    main()
