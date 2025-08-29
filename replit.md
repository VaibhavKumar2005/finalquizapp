# AI Quiz Generator

## Overview

An AI-powered quiz generation application built with Streamlit that creates quizzes from PDF documents. The system extracts text from uploaded PDFs and uses Google's Gemini AI to automatically generate multiple-choice and true/false questions with customizable difficulty levels. Users can export generated quizzes as PDFs or text files for easy distribution and use.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

### August 28, 2025
- Successfully built complete AI Quiz Generator application with red-themed UI
- Integrated Google Gemini API for intelligent question generation  
- Implemented PDF upload and text extraction using PyPDF2
- Added quiz configuration controls (number of questions, difficulty levels)
- Created export functionality for PDF and text formats
- Fixed API connection issues and optimized question generation prompts
- Application fully functional and ready for deployment

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application with custom CSS styling
- **UI Design**: Red-themed interface with gradient headers and card-based layout
- **User Flow**: File upload → PDF processing → AI quiz generation → export options
- **Responsive Design**: Wide layout with expandable sidebar for configuration options

### Backend Architecture
- **PDF Processing**: Multi-layered text extraction using PyPDF2 as primary method with fallback to unstructured library
- **AI Integration**: Google Gemini API for intelligent question generation with structured prompts
- **Question Types**: Support for multiple-choice (70% distribution) and true/false (30% distribution) questions
- **Difficulty Scaling**: Three-tier difficulty system (Easy, Medium, Hard) with AI-driven content adaptation

### Export System
- **PDF Generation**: ReportLab-based PDF creation with custom styling and formatting
- **Text Export**: Plain text format for simple distribution
- **File Handling**: Temporary file management for secure upload processing

### Error Handling
- **Graceful Degradation**: Multiple extraction methods with fallback options
- **User Feedback**: Comprehensive error messages and processing status indicators
- **Logging**: Structured logging for debugging and monitoring

## External Dependencies

### AI Services
- **Google Gemini API**: Primary AI service for question generation and content analysis
- **Authentication**: API key-based authentication system

### PDF Processing Libraries
- **PyPDF2**: Primary PDF text extraction library
- **unstructured**: Optional enhanced PDF processing library for complex document layouts

### Document Generation
- **ReportLab**: PDF generation library for creating formatted quiz exports
- **BytesIO**: In-memory file handling for export functionality

### Web Framework
- **Streamlit**: Complete web application framework with built-in UI components and file handling