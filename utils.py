from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from io import BytesIO
from typing import List, Dict, Any
import datetime

def export_quiz_to_pdf(quiz_data: List[Dict[str, Any]]) -> BytesIO:
    """
    Export quiz data to a formatted PDF.
    
    Args:
        quiz_data: List of question dictionaries
        
    Returns:
        BytesIO buffer containing the PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch, bottomMargin=1*inch)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=HexColor('#dc2626'),
        alignment=1  # Center alignment
    )
    
    question_style = ParagraphStyle(
        'QuestionStyle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=20,
        spaceAfter=10,
        textColor=HexColor('#1f2937')
    )
    
    option_style = ParagraphStyle(
        'OptionStyle',
        parent=styles['Normal'],
        fontSize=12,
        leftIndent=20,
        spaceAfter=5
    )
    
    answer_style = ParagraphStyle(
        'AnswerStyle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=HexColor('#059669'),
        spaceBefore=10,
        spaceAfter=15,
        backColor=HexColor('#f0fdf4'),
        borderColor=HexColor('#22c55e'),
        borderWidth=1,
        borderPadding=5
    )
    
    # Build the PDF content
    story = []
    
    # Title
    title = Paragraph("🎯 AI Generated Quiz", title_style)
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Metadata
    current_date = datetime.datetime.now().strftime("%B %d, %Y")
    metadata = Paragraph(f"Generated on: {current_date} | Questions: {len(quiz_data)}", styles['Normal'])
    story.append(metadata)
    story.append(Spacer(1, 30))
    
    # Instructions
    instructions = Paragraph(
        "<b>Instructions:</b> Choose the best answer for each question. "
        "For True/False questions, circle T for True or F for False.",
        styles['Normal']
    )
    story.append(instructions)
    story.append(Spacer(1, 20))
    
    # Questions
    for i, question in enumerate(quiz_data, 1):
        # Question number and text
        question_text = f"<b>Question {i}:</b> {question['question']}"
        story.append(Paragraph(question_text, question_style))
        
        if question['type'] == 'multiple_choice':
            # Multiple choice options
            for j, option in enumerate(question['options']):
                option_letter = chr(65 + j)  # A, B, C, D
                option_text = f"{option_letter}. {option}"
                story.append(Paragraph(option_text, option_style))
        
        elif question['type'] == 'true_false':
            # True/False options
            story.append(Paragraph("A. True", option_style))
            story.append(Paragraph("B. False", option_style))
        
        story.append(Spacer(1, 10))
    
    # Answer Key (on separate page)
    story.append(PageBreak())
    
    answer_title = Paragraph("📋 Answer Key", title_style)
    story.append(answer_title)
    story.append(Spacer(1, 20))
    
    for i, question in enumerate(quiz_data, 1):
        answer_text = f"<b>Question {i}:</b> {question['correct_answer']}"
        if 'explanation' in question and question['explanation']:
            answer_text += f"<br/><i>Explanation: {question['explanation']}</i>"
        
        story.append(Paragraph(answer_text, answer_style))
        story.append(Spacer(1, 5))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def export_quiz_to_text(quiz_data: List[Dict[str, Any]]) -> str:
    """
    Export quiz data to a formatted text string.
    
    Args:
        quiz_data: List of question dictionaries
        
    Returns:
        Formatted text string
    """
    lines = []
    current_date = datetime.datetime.now().strftime("%B %d, %Y")
    
    # Header
    lines.append("=" * 60)
    lines.append("🎯 AI GENERATED QUIZ")
    lines.append("=" * 60)
    lines.append(f"Generated on: {current_date}")
    lines.append(f"Total Questions: {len(quiz_data)}")
    lines.append("")
    lines.append("INSTRUCTIONS:")
    lines.append("Choose the best answer for each question.")
    lines.append("For True/False questions, select True or False.")
    lines.append("")
    lines.append("=" * 60)
    lines.append("QUESTIONS")
    lines.append("=" * 60)
    lines.append("")
    
    # Questions
    for i, question in enumerate(quiz_data, 1):
        lines.append(f"Question {i}: {question['question']}")
        lines.append("")
        
        if question['type'] == 'multiple_choice':
            for j, option in enumerate(question['options']):
                option_letter = chr(65 + j)  # A, B, C, D
                lines.append(f"   {option_letter}. {option}")
        
        elif question['type'] == 'true_false':
            lines.append("   A. True")
            lines.append("   B. False")
        
        lines.append("")
        lines.append("-" * 40)
        lines.append("")
    
    # Answer Key
    lines.append("")
    lines.append("=" * 60)
    lines.append("ANSWER KEY")
    lines.append("=" * 60)
    lines.append("")
    
    for i, question in enumerate(quiz_data, 1):
        lines.append(f"Question {i}: {question['correct_answer']}")
        if 'explanation' in question and question['explanation']:
            lines.append(f"   Explanation: {question['explanation']}")
        lines.append("")
    
    return "\n".join(lines)

def validate_question_data(question: Dict[str, Any]) -> bool:
    """
    Validate a single question's data structure.
    
    Args:
        question: Question dictionary to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['question', 'correct_answer', 'type']
    
    # Check required fields
    if not all(field in question for field in required_fields):
        return False
    
    # Check question type specific requirements
    if question['type'] == 'multiple_choice':
        if 'options' not in question:
            return False
        if not isinstance(question['options'], list) or len(question['options']) != 4:
            return False
        if question['correct_answer'] not in ['A', 'B', 'C', 'D']:
            return False
    
    elif question['type'] == 'true_false':
        if question['correct_answer'] not in ['True', 'False']:
            return False
    
    else:
        return False  # Unknown question type
    
    return True

def format_quiz_for_display(quiz_data: List[Dict[str, Any]]) -> str:
    """
    Format quiz data for display in Streamlit.
    
    Args:
        quiz_data: List of question dictionaries
        
    Returns:
        Formatted HTML string
    """
    html_parts = []
    
    for i, question in enumerate(quiz_data, 1):
        html_parts.append(f'<div class="quiz-question">')
        html_parts.append(f'<h4>Question {i}: {question["question"]}</h4>')
        
        if question['type'] == 'multiple_choice':
            html_parts.append('<ul>')
            for j, option in enumerate(question['options']):
                option_letter = chr(65 + j)
                is_correct = option_letter == question['correct_answer']
                style = 'style="color: #22c55e; font-weight: bold;"' if is_correct else ''
                html_parts.append(f'<li {style}>{option_letter}. {option}</li>')
            html_parts.append('</ul>')
        
        elif question['type'] == 'true_false':
            correct = question['correct_answer']
            true_style = 'style="color: #22c55e; font-weight: bold;"' if correct == 'True' else ''
            false_style = 'style="color: #22c55e; font-weight: bold;"' if correct == 'False' else ''
            html_parts.append(f'<p {true_style}>True</p>')
            html_parts.append(f'<p {false_style}>False</p>')
        
        if 'explanation' in question:
            html_parts.append(f'<p><strong>Explanation:</strong> {question["explanation"]}</p>')
        
        html_parts.append('</div><hr>')
    
    return ''.join(html_parts)

def get_quiz_statistics(quiz_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Get statistics about the quiz data.
    
    Args:
        quiz_data: List of question dictionaries
        
    Returns:
        Dictionary with quiz statistics
    """
    if not quiz_data:
        return {}
    
    total_questions = len(quiz_data)
    mc_count = sum(1 for q in quiz_data if q['type'] == 'multiple_choice')
    tf_count = sum(1 for q in quiz_data if q['type'] == 'true_false')
    
    # Count explanations
    with_explanations = sum(1 for q in quiz_data if q.get('explanation', '').strip())
    
    return {
        'total_questions': total_questions,
        'multiple_choice': mc_count,
        'true_false': tf_count,
        'with_explanations': with_explanations,
        'mc_percentage': round((mc_count / total_questions) * 100, 1) if total_questions > 0 else 0,
        'tf_percentage': round((tf_count / total_questions) * 100, 1) if total_questions > 0 else 0
    }
