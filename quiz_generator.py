import json
import logging
import re
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
import os

class QuizGenerator:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the QuizGenerator with Gemini API."""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is required")
        
        self.client = genai.Client(api_key=self.api_key)
    
    def _extract_json_from_response(self, response_text: str, question_type: str) -> List[Dict[str, Any]]:
        """Extract and parse JSON from API response with robust error handling."""
        try:
            # Clean the response text
            text = response_text.strip()
            
            # Remove markdown code blocks
            if text.startswith('```json'):
                text = text[7:]
            elif text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
            text = text.strip()
            
            # Find JSON array boundaries
            start_idx = text.find('[')
            end_idx = text.rfind(']') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_text = text[start_idx:end_idx]
                
                # Try parsing the JSON
                try:
                    questions_data = json.loads(json_text)
                    if isinstance(questions_data, list):
                        valid_questions = []
                        for q in questions_data:
                            if isinstance(q, dict) and 'question' in q and 'correct_answer' in q:
                                q['type'] = question_type
                                valid_questions.append(q)
                        return valid_questions
                except json.JSONDecodeError:
                    # Try fixing common JSON issues
                    fixed_text = json_text.replace("'", '"')
                    # Fix trailing commas
                    fixed_text = re.sub(r',(\s*[}\]])', r'\1', fixed_text)
                    try:
                        questions_data = json.loads(fixed_text)
                        if isinstance(questions_data, list):
                            valid_questions = []
                            for q in questions_data:
                                if isinstance(q, dict) and 'question' in q and 'correct_answer' in q:
                                    q['type'] = question_type
                                    valid_questions.append(q)
                            return valid_questions
                    except json.JSONDecodeError as e:
                        logging.error(f"JSON parsing failed after fixes: {e}")
                        logging.error(f"Problematic JSON: {fixed_text}")
            
            return []
            
        except Exception as e:
            logging.error(f"Error extracting JSON: {e}")
            return []
    
    def generate_quiz(self, text: str, num_questions: int = 10, 
                     difficulty: str = "Medium", question_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Generate quiz questions from the provided text.
        
        Args:
            text: The source text to generate questions from
            num_questions: Number of questions to generate
            difficulty: Difficulty level (Easy, Medium, Hard)
            question_types: Types of questions to include
        
        Returns:
            List of question dictionaries
        """
        if question_types is None:
            question_types = ["Multiple Choice", "True/False"]
        
        # Calculate distribution of question types
        mc_count = 0
        tf_count = 0
        
        if "Multiple Choice" in question_types and "True/False" in question_types:
            mc_count = int(num_questions * 0.7)  # 70% multiple choice
            tf_count = num_questions - mc_count  # 30% true/false
        elif "Multiple Choice" in question_types:
            mc_count = num_questions
        elif "True/False" in question_types:
            tf_count = num_questions
        
        questions = []
        
        # Generate Multiple Choice Questions
        if mc_count > 0:
            mc_questions = self._generate_multiple_choice_questions(text, mc_count, difficulty)
            questions.extend(mc_questions)
        
        # Generate True/False Questions
        if tf_count > 0:
            tf_questions = self._generate_true_false_questions(text, tf_count, difficulty)
            questions.extend(tf_questions)
        
        return questions
    
    def _generate_multiple_choice_questions(self, text: str, count: int, difficulty: str) -> List[Dict[str, Any]]:
        """Generate multiple choice questions with retry logic."""
        system_prompt = f"""Create exactly {count} multiple-choice questions from the text provided.

CRITICAL: You must create exactly {count} questions, no more, no less.

Return ONLY a valid JSON array in this exact format:
[
  {{
    "question": "Your question here?",
    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
    "correct_answer": "A",
    "explanation": "Brief explanation"
  }}
]

Requirements:
- Exactly {count} questions in the JSON array
- Difficulty level: {difficulty}
- Each question has exactly 4 options
- Correct answer must be A, B, C, or D
- Include brief explanations
- Focus on key concepts from the provided text
- Return valid JSON only, no other text"""
        
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"{system_prompt}\n\nText to analyze:\n{text}",
                    config=types.GenerateContentConfig(
                        temperature=0.7,
                        max_output_tokens=8000
                    )
                )
                
                if response.text:
                    questions = self._extract_json_from_response(response.text, 'multiple_choice')
                    if len(questions) == count:
                        return questions
                    elif len(questions) > 0:
                        # If we got some questions but not the exact count, return what we have
                        logging.warning(f"Generated {len(questions)} questions instead of {count}")
                        return questions[:count]  # Take only the requested number
                
            except Exception as e:
                logging.error(f"Error generating multiple choice questions (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    return []
        
        return []
    
    def _generate_true_false_questions(self, text: str, count: int, difficulty: str) -> List[Dict[str, Any]]:
        """Generate true/false questions with retry logic."""
        system_prompt = f"""Create exactly {count} true/false questions from the text provided.

CRITICAL: You must create exactly {count} questions, no more, no less.

Return ONLY a valid JSON array in this exact format:
[
  {{
    "question": "Statement to evaluate as true or false",
    "correct_answer": "True",
    "explanation": "Brief explanation"
  }}
]

Requirements:
- Exactly {count} questions in the JSON array
- Difficulty level: {difficulty}
- Correct answer must be either "True" or "False"
- Mix of true and false answers
- Include brief explanations
- Focus on key facts from the provided text
- Return valid JSON only, no other text"""
        
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"{system_prompt}\n\nText to analyze:\n{text}",
                    config=types.GenerateContentConfig(
                        temperature=0.7,
                        max_output_tokens=6000
                    )
                )
                
                if response.text:
                    questions = self._extract_json_from_response(response.text, 'true_false')
                    if len(questions) == count:
                        return questions
                    elif len(questions) > 0:
                        # If we got some questions but not the exact count, return what we have
                        logging.warning(f"Generated {len(questions)} questions instead of {count}")
                        return questions[:count]  # Take only the requested number
                
            except Exception as e:
                logging.error(f"Error generating true/false questions (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    return []
        
        return []
    
    def validate_quiz_data(self, quiz_data: List[Dict[str, Any]]) -> bool:
        """Validate the structure of quiz data."""
        required_fields = ['question', 'correct_answer', 'type']
        
        for question in quiz_data:
            if not all(field in question for field in required_fields):
                return False
            
            if question['type'] == 'multiple_choice':
                if 'options' not in question or len(question['options']) != 4:
                    return False
                if question['correct_answer'] not in ['A', 'B', 'C', 'D']:
                    return False
            
            elif question['type'] == 'true_false':
                if question['correct_answer'] not in ['True', 'False']:
                    return False
        
        return True
