import os
import tempfile
import logging
from typing import Optional
import PyPDF2
from io import BytesIO

# Note: unstructured library would be ideal but may not be available
# This implementation uses PyPDF2 as a fallback with enhanced text extraction

class PDFProcessor:
    def __init__(self):
        """Initialize the PDF processor."""
        self.logger = logging.getLogger(__name__)
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF file using multiple methods for best results.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text content
        """
        try:
            # Use PyPDF2 for text extraction
            text = self._extract_with_pypdf2(file_path)
            if text and len(text.strip()) > 50:
                return text
            
            # Try unstructured library as fallback (if available)
            text = self._extract_with_unstructured(file_path)
            if text and len(text.strip()) > 100:  # Minimum content threshold
                return text
            
            return "No readable text could be extracted from this PDF."
            
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF: {e}")
            return f"Error processing PDF: {str(e)}"
    
    def _extract_with_unstructured(self, file_path: str) -> Optional[str]:
        """Extract text using unstructured library (if available)."""
        try:
            # Import unstructured libraries if available
            from unstructured.partition.pdf import partition_pdf
            from unstructured.chunking.title import chunk_by_title
            
            # Partition the PDF
            elements = partition_pdf(
                filename=file_path,
                strategy="fast",  # Use fast strategy for better performance
                infer_table_structure=True,
                extract_images_in_pdf=False,
            )
            
            # Extract text from elements
            text_content = []
            for element in elements:
                if hasattr(element, 'text') and element.text.strip():
                    text_content.append(element.text.strip())
            
            return "\n\n".join(text_content)
            
        except ImportError:
            self.logger.info("Unstructured library not available")
            return None
        except Exception as e:
            self.logger.error(f"Error with unstructured extraction: {e}")
            return None
    
    def _extract_with_pypdf2(self, file_path: str) -> str:
        """Extract text using PyPDF2 as fallback."""
        try:
            text_content = []
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract text from each page
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():
                            # Clean up the text
                            cleaned_text = self._clean_extracted_text(page_text)
                            if cleaned_text:
                                text_content.append(f"--- Page {page_num + 1} ---\n{cleaned_text}")
                    except Exception as e:
                        self.logger.warning(f"Error extracting text from page {page_num + 1}: {e}")
                        continue
            
            return "\n\n".join(text_content)
            
        except Exception as e:
            self.logger.error(f"Error with PyPDF2 extraction: {e}")
            raise
    
    def _clean_extracted_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        if not text:
            return ""
        
        # Basic text cleaning
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line and len(line) > 2:  # Filter out very short lines
                # Remove excessive whitespace
                line = ' '.join(line.split())
                cleaned_lines.append(line)
        
        # Join lines back together
        cleaned_text = ' '.join(cleaned_lines)
        
        # Additional cleaning
        cleaned_text = cleaned_text.replace('\x00', '')  # Remove null characters
        cleaned_text = ' '.join(cleaned_text.split())    # Normalize whitespace
        
        return cleaned_text
    
    def extract_text_from_uploaded_file(self, uploaded_file) -> str:
        """
        Extract text from Streamlit uploaded file object.
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            Extracted text content
        """
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            # Extract text
            text = self.extract_text_from_pdf(tmp_file_path)
            
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
            return text
            
        except Exception as e:
            self.logger.error(f"Error processing uploaded file: {e}")
            return f"Error processing uploaded file: {str(e)}"
    
    def validate_pdf(self, file_path: str) -> bool:
        """
        Validate if the file is a proper PDF.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            True if valid PDF, False otherwise
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                # Try to access the first page
                if len(pdf_reader.pages) > 0:
                    _ = pdf_reader.pages[0]
                    return True
            return False
        except Exception:
            return False
    
    def get_pdf_info(self, file_path: str) -> dict:
        """
        Get basic information about the PDF.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary with PDF information
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                info = {
                    'num_pages': len(pdf_reader.pages),
                    'title': '',
                    'author': '',
                    'subject': '',
                    'file_size': os.path.getsize(file_path)
                }
                
                # Try to get metadata
                if pdf_reader.metadata:
                    info['title'] = pdf_reader.metadata.get('/Title', '')
                    info['author'] = pdf_reader.metadata.get('/Author', '')
                    info['subject'] = pdf_reader.metadata.get('/Subject', '')
                
                return info
                
        except Exception as e:
            self.logger.error(f"Error getting PDF info: {e}")
            return {'error': str(e)}
