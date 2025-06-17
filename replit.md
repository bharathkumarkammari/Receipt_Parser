# Costco Receipt Parser

## Overview

This is a Flask-based web application that allows users to upload Costco receipt PDFs and extract purchase data from them. The application uses PDF processing to parse receipt content and stores the extracted data in a JSON file for persistence. It features a responsive web interface with Bootstrap styling and handles file uploads with validation.

## System Architecture

The application follows a simple monolithic architecture with a Flask backend serving both API endpoints and static web pages. The system is designed for single-user deployment with file-based data storage.

### Core Components:
- **Flask Web Framework**: Handles HTTP requests, routing, and template rendering
- **PDF Processing**: Uses pdfplumber library to extract text from uploaded PDF files
- **File Storage**: JSON-based data persistence for receipt records
- **Frontend**: Bootstrap-based responsive UI with JavaScript enhancements

## Key Components

### Backend (Flask Application)
- **main.py**: Entry point that runs the Flask development server
- **app.py**: Main application logic including:
  - File upload handling and validation
  - PDF text extraction functionality (incomplete implementation)
  - JSON data persistence operations
  - Route definitions and request handling

### Frontend
- **templates/index.html**: Main web interface with upload form and receipt display
- **static/style.css**: Custom CSS styling complementing Bootstrap theme
- **static/script.js**: Client-side validation and UI interactions

### Data Storage
- **receipts_data.json**: JSON file storing extracted receipt data
- **uploads/**: Directory for storing uploaded PDF files

### Configuration
- **pyproject.toml**: Python project dependencies and metadata
- **.replit**: Replit-specific configuration for deployment and development
- **uv.lock**: Dependency lock file for reproducible builds

## Data Flow

1. **Upload Process**:
   - User selects PDF file through web interface
   - Client-side validation checks file type and size
   - File is uploaded to Flask backend via POST request
   - Server validates file and saves to uploads directory

2. **PDF Processing**:
   - PDF text extraction using pdfplumber library
   - Text parsing to identify receipt items and metadata
   - Data structuring for storage

3. **Data Persistence**:
   - Extracted data is loaded from existing JSON file
   - New receipt data is appended to the collection
   - Updated data is saved back to JSON file

4. **Display**:
   - Web interface loads and displays stored receipt data
   - Bootstrap components provide responsive layout
   - JavaScript enhances user interactions

## External Dependencies

### Python Packages:
- **Flask**: Web framework for handling HTTP requests and rendering templates
- **pdfplumber**: PDF text extraction and processing
- **Werkzeug**: WSGI utilities for secure file handling
- **Gunicorn**: WSGI HTTP server for production deployment
- **psycopg2-binary**: PostgreSQL adapter (currently unused but configured)
- **Flask-SQLAlchemy**: ORM for database operations (currently unused but configured)
- **email-validator**: Email validation utilities (currently unused but configured)

### Frontend Dependencies:
- **Bootstrap**: CSS framework for responsive design
- **Font Awesome**: Icon library for UI enhancements

## Deployment Strategy

The application is configured for deployment on Replit with autoscaling capabilities:

- **Development**: Flask development server with debug mode enabled
- **Production**: Gunicorn WSGI server with multiple worker processes
- **Platform**: Replit with Nix package management for system dependencies
- **Scaling**: Autoscale deployment target for handling variable load

### Deployment Configuration:
- Gunicorn binds to 0.0.0.0:5000 with port reuse and auto-reload
- OpenSSL and PostgreSQL system packages are available
- Python 3.11 runtime environment

## Changelog
- June 17, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.