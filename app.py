import streamlit as st
import os
from quiz_generator import QuizGenerator
from pdf_processor import PDFProcessor
from utils import export_quiz_to_pdf, export_quiz_to_text
import tempfile

# Page configuration
st.set_page_config(
    page_title="AI Quiz Generator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for red theme
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #dc2626, #b91c1c);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .main-header h1 {
        color: white !important;
        margin: 0;
        font-size: 3rem;
        font-weight: bold;
    }
    
    .main-header p {
        color: #fecaca !important;
        margin: 0.5rem 0 0 0;
        font-size: 1.2rem;
    }
    
    .quiz-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #dc2626;
        box-shadow: 0 2px 10px rgba(220, 38, 38, 0.1);
        margin-bottom: 1rem;
    }
    
    .question-number {
        background: #dc2626;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 1rem;
    }
    
    .correct-answer {
        background: #dcfce7;
        border: 1px solid #22c55e;
        padding: 0.5rem;
        border-radius: 5px;
        margin-top: 0.5rem;
    }
    
    .sidebar-section {
        background: #fef2f2;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #fecaca;
        margin-bottom: 1rem;
    }
    
    .success-message {
        background: #dcfce7;
        border: 1px solid #22c55e;
        color: #15803d;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .error-message {
        background: #fef2f2;
        border: 1px solid #fecaca;
        color: #dc2626;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #dc2626, #b91c1c);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #b91c1c, #991b1b);
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(220, 38, 38, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🎯 AI Quiz Generator</h1>
    <p>Transform your PDF chapters into engaging quizzes with AI-powered question generation</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = None
if 'pdf_processed' not in st.session_state:
    st.session_state.pdf_processed = False
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = ""

# Sidebar
with st.sidebar:
    st.markdown("### 📋 Quiz Configuration")
    
    # PDF Upload
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("**📄 Upload PDF Chapter**")
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload a PDF chapter to generate quiz questions from"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Quiz Settings
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("**⚙️ Quiz Settings**")
    
    num_questions = st.slider(
        "Number of Questions",
        min_value=5,
        max_value=50,
        value=15,
        step=5,
        help="Select how many questions to generate"
    )
    
    difficulty_level = st.selectbox(
        "Difficulty Level",
        options=["Easy", "Medium", "Hard"],
        index=1,
        help="Choose the difficulty level for questions"
    )
    
    question_types = st.multiselect(
        "Question Types",
        options=["Multiple Choice", "True/False"],
        default=["Multiple Choice", "True/False"],
        help="Select types of questions to generate"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # API Configuration
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("**🔑 API Configuration**")
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        st.warning("⚠️ Gemini API key not found in environment variables")
        api_key = st.text_input(
            "Enter Gemini API Key",
            type="password",
            help="Get your API key from Google AI Studio"
        )
    else:
        st.success("✅ API key loaded from environment")
    st.markdown('</div>', unsafe_allow_html=True)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # Process PDF when uploaded
    if uploaded_file is not None and not st.session_state.pdf_processed:
        with st.spinner("🔄 Processing PDF..."):
            try:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name
                
                # Process PDF
                pdf_processor = PDFProcessor()
                extracted_text = pdf_processor.extract_text_from_pdf(tmp_file_path)
                
                if extracted_text.strip():
                    st.session_state.extracted_text = extracted_text
                    st.session_state.pdf_processed = True
                    st.markdown('<div class="success-message">✅ PDF processed successfully!</div>', unsafe_allow_html=True)
                    
                    # Show text preview
                    with st.expander("📖 Preview Extracted Text"):
                        st.text_area(
                            "Extracted content:",
                            value=extracted_text[:1000] + "..." if len(extracted_text) > 1000 else extracted_text,
                            height=200,
                            disabled=True
                        )
                else:
                    st.markdown('<div class="error-message">❌ No text could be extracted from the PDF. Please ensure the PDF contains readable text.</div>', unsafe_allow_html=True)
                
                # Cleanup
                os.unlink(tmp_file_path)
                
            except Exception as e:
                st.markdown(f'<div class="error-message">❌ Error processing PDF: {str(e)}</div>', unsafe_allow_html=True)
    
    # Generate Quiz Button
    if st.session_state.pdf_processed and api_key:
        st.markdown("### 🚀 Generate Quiz")
        
        if st.button("🎯 Generate Quiz Questions", use_container_width=True):
            with st.spinner("🤖 Generating quiz questions with AI..."):
                try:
                    quiz_generator = QuizGenerator(api_key)
                    quiz_data = quiz_generator.generate_quiz(
                        text=st.session_state.extracted_text,
                        num_questions=num_questions,
                        difficulty=difficulty_level,
                        question_types=question_types
                    )
                    
                    if quiz_data:
                        st.session_state.quiz_data = quiz_data
                        st.markdown('<div class="success-message">🎉 Quiz generated successfully!</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="error-message">❌ Failed to generate quiz. Please try again.</div>', unsafe_allow_html=True)
                        
                except Exception as e:
                    st.markdown(f'<div class="error-message">❌ Error generating quiz: {str(e)}</div>', unsafe_allow_html=True)

with col2:
    # Download Section
    if st.session_state.quiz_data:
        st.markdown("### 📥 Download Quiz")
        
        col_pdf, col_txt = st.columns(2)
        
        with col_pdf:
            if st.button("📄 Download PDF", use_container_width=True):
                try:
                    pdf_buffer = export_quiz_to_pdf(st.session_state.quiz_data)
                    st.download_button(
                        label="💾 Save PDF",
                        data=pdf_buffer,
                        file_name="quiz.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Error creating PDF: {str(e)}")
        
        with col_txt:
            if st.button("📝 Download Text", use_container_width=True):
                try:
                    text_content = export_quiz_to_text(st.session_state.quiz_data)
                    st.download_button(
                        label="💾 Save Text",
                        data=text_content,
                        file_name="quiz.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Error creating text file: {str(e)}")

# Display Generated Quiz
if st.session_state.quiz_data:
    st.markdown("### 📝 Generated Quiz")
    
    for i, question in enumerate(st.session_state.quiz_data, 1):
        st.markdown(f"""
        <div class="quiz-card">
            <div class="question-number">Question {i}</div>
            <h4>{question['question']}</h4>
        """, unsafe_allow_html=True)
        
        if question['type'] == 'multiple_choice':
            for j, option in enumerate(question['options']):
                option_letter = chr(65 + j)  # A, B, C, D
                is_correct = option_letter == question['correct_answer']
                style = "font-weight: bold; color: #22c55e;" if is_correct else ""
                st.markdown(f"<p style='{style}'>{option_letter}. {option}</p>", unsafe_allow_html=True)
        
        elif question['type'] == 'true_false':
            correct_answer = question['correct_answer']
            st.markdown(f"<p><strong>True</strong> {'✅' if correct_answer == 'True' else ''}</p>", unsafe_allow_html=True)
            st.markdown(f"<p><strong>False</strong> {'✅' if correct_answer == 'False' else ''}</p>", unsafe_allow_html=True)
        
        st.markdown(f"""
            <div class="correct-answer">
                <strong>Correct Answer:</strong> {question['correct_answer']}
                <br><strong>Explanation:</strong> {question.get('explanation', 'No explanation provided.')}
            </div>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6b7280; padding: 2rem;">
    <p>🎓 AI Quiz Generator - Powered by Gemini AI | Made for Educators</p>
</div>
""", unsafe_allow_html=True)
