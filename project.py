import streamlit as st
from docx import Document
import openai
from dotenv import load_dotenv
import os
import fitz  # PyMuPDF

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to extract text from a Word document
def extract_text_from_docx(docx_file):
    doc = Document(docx_file)
    return "\n".join(para.text for para in doc.paragraphs)

# Function to extract text from a PDF document (using PyMuPDF)
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = "".join(page.get_text("text") for page in doc)
    return text

# Function to grade an essay using OpenAI
def grade_essay(essay_text, rubric_text):
    prompt = f"I am a college level student. Grade the following homework based on this rubric and just output the score:\n{rubric_text}\n\nEssay:\n{essay_text}. Try to avoid giving a perfect grade I am looking for feedback"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a homework grading assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
            temperature=0.8,
        )
        grading_feedback = response.choices[0].message['content'].strip()
        return grading_feedback
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Streamlit UI
st.title("AutoGrader")
st.subheader("Upload your homework and your rubric and get a projected score with feedback on what to improve on.")

essay_file = st.file_uploader("Upload your homework (Word or PDF)", type=["docx", "pdf"])
rubric_file = st.file_uploader("Upload your rubric (Word or PDF)", type=["docx", "pdf"])

if essay_file and rubric_file:
    essay_text = extract_text_from_pdf(essay_file) if essay_file.type == "application/pdf" else extract_text_from_docx(essay_file)
    rubric_text = extract_text_from_pdf(rubric_file) if rubric_file.type == "application/pdf" else extract_text_from_docx(rubric_file)

    st.subheader("Essay Text")
    st.text(essay_text)

    st.subheader("Rubric Text")
    st.text(rubric_text)

    st.subheader("Grading Results")
    grading_feedback = grade_essay(essay_text, rubric_text)
    st.write(grading_feedback)
else:
    st.warning("Please upload both the homework and the rubric.")
