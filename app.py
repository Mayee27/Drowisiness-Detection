# Standard imports
from dotenv import load_dotenv
import base64
import os
import io
from PIL import Image
import pdf2image
import google.generativeai as genai
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Streamlit import
import streamlit as st

# Streamlit configuration (MUST BE FIRST Streamlit command)
st.set_page_config(
    page_title="ATS Resume Expert",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load environment variables
load_dotenv()

# Configure the Generative AI API
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    st.error("Google API Key not found. Please set it in your environment variables.")
    st.stop()

genai.configure(api_key=API_KEY)

# Helper Functions
def get_gemini_response(input_text, pdf_content, prompt):
    """Get the response from the Gemini model based on input text and PDF content."""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([input_text, pdf_content, prompt])
        return response.text
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        return None


def convert_pdf_to_images(uploaded_file):
    """Convert the first page of the uploaded PDF file to an image and return as base64 encoded."""
    try:
        images = pdf2image.convert_from_bytes(uploaded_file.read())
        if images:
            img = images[0]  # Use the first page image as an example
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()
            return {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()
            }
        else:
            return None
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return None


def create_wordcloud(text):
    """Generate and display a word cloud from the provided text."""
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)


# UI Layout
st.sidebar.title("ATS Resume Tracker")
st.sidebar.info("Optimize your resume to match job descriptions with ATS insights.")

st.title("ATS Resume Tracking System")
st.markdown(
    """
    Welcome to the **ATS Resume Tracking System**! Use this tool to:
    - Evaluate your resume against a job description.
    - Get a percentage match with keywords and improvement tips.
    - Visualize job description keywords with a word cloud.
    """
)

# Input Fields
st.subheader("Provide Job Details and Resume")
input_text = st.text_area(
    "Enter Job Description:", 
    key="job_desc", 
    placeholder="Paste the job description here..."
)
uploaded_file = st.file_uploader(
    "Upload your Resume (PDF):", 
    type=["pdf"], 
    help="Ensure the uploaded file is in PDF format."
)

# Prompts
review_prompt = """
You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against the job description. 
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

match_prompt = """
You are a skilled ATS (Applicant Tracking System) scanner. Evaluate the resume against the provided job description. 
Provide the match percentage, missing keywords, and final feedback.
"""

# Buttons
col1, col2, col3 = st.columns(3)
with col1:
    submit_review = st.button("Evaluate Resume")
with col2:
    submit_match = st.button("Percentage Match")
with col3:
    generate_wordcloud = st.button("Generate Word Cloud")

# Process User Inputs
if uploaded_file is not None:
    st.success("Resume uploaded successfully!")
    pdf_content = convert_pdf_to_images(uploaded_file)
else:
    pdf_content = None

# Actions
if submit_review and pdf_content:
    response = get_gemini_response(input_text, pdf_content, review_prompt)
    if response:
        st.subheader("Resume Evaluation:")
        st.write(response)
elif submit_review:
    st.warning("Please upload a resume to proceed.")

if submit_match and pdf_content:
    response = get_gemini_response(input_text, pdf_content, match_prompt)
    if response:
        st.subheader("Percentage Match Results:")
        st.write(response)
elif submit_match:
    st.warning("Please upload a resume to proceed.")

if generate_wordcloud and input_text:
    st.subheader("Job Description Word Cloud:")
    create_wordcloud(input_text)
