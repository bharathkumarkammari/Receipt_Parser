import os
import json
import re
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import pdfplumber
from werkzeug.utils import secure_filename

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "fallback_secret_key_for_development")

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
DATA_FILE = 'receipts_data.json'

# Create upload directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_receipts_data():
    """Load existing receipts data from JSON file"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        logging.error(f"Error loading receipts data: {e}")
        return []

def save_receipts_data(data):
    """Save receipts data to JSON file"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logging.error(f"Error saving receipts data: {e}")
        return False

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using pdfplumber"""
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {e}")
        return None

def parse_costco_receipt(text):
    """Parse Costco receipt text to extract items, prices, and totals"""
    try:
        lines = text.split('\n')
        items = []
        subtotal = None
        tax = None
        total = None
        
        # Regex patterns for Costco receipts
        item_pattern = r'^(\d{6,8})\s+(.+?)(?:\s+(\d+\.?\d*)\s*$)'
        discount_pattern = r'^\s*(\d+\.?\d*)-\s*$'
        price_pattern = r'\s+(\d+\.\d{2})\s*$'
        subtotal_pattern = r'SUBTOTAL\s+(\d+\.\d{2})'
        tax_pattern = r'TAX\s+(\d+\.\d{2})'
        total_pattern = r'TOTAL\s+(\d+\.\d{2})'
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Check for subtotal, tax, total
            subtotal_match = re.search(subtotal_pattern, line, re.IGNORECASE)
            if subtotal_match:
                subtotal = float(subtotal_match.group(1))
                i += 1
                continue
                
            tax_match = re.search(tax_pattern, line, re.IGNORECASE)
            if tax_match:
                tax = float(tax_match.group(1))
                i += 1
                continue
                
            total_match = re.search(total_pattern, line, re.IGNORECASE)
            if total_match:
                total = float(total_match.group(1))
                i += 1
                continue
            
            # Check for item lines
            # Pattern 1: Item code and name on same line with price
            item_match = re.match(r'^(\d{6,8})\s+(.+?)\s+(\d+\.\d{2})\s*$', line)
            if item_match:
                item_code = item_match.group(1)
                item_name = item_match.group(2).strip()
                price = float(item_match.group(3))
                discount = 0.0
                
                # Check next line for discount
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    discount_match = re.match(discount_pattern, next_line)
                    if discount_match:
                        discount = float(discount_match.group(1))
                        i += 1  # Skip the discount line
                
                items.append({
                    'item_code': item_code,
                    'item_name': item_name,
                    'price': price,
                    'discount': discount
                })
                i += 1
                continue
            
            # Pattern 2: Item code and partial name, with continuation on next line
            item_code_match = re.match(r'^(\d{6,8})\s+(.+)$', line)
            if item_code_match and not re.search(r'\d+\.\d{2}$', line):
                item_code = item_code_match.group(1)
                item_name = item_code_match.group(2).strip()
                price = 0.0
                discount = 0.0
                
                # Look for price in next few lines
                j = i + 1
                while j < len(lines) and j < i + 3:
                    next_line = lines[j].strip()
                    
                    # Check if this line has a price
                    price_match = re.search(r'(\d+\.\d{2})\s*$', next_line)
                    if price_match:
                        price = float(price_match.group(1))
                        # Remove price from line and add to item name
                        name_part = re.sub(r'\s+\d+\.\d{2}\s*$', '', next_line).strip()
                        if name_part:
                            item_name += " " + name_part
                        
                        # Check for discount on following line
                        if j + 1 < len(lines):
                            discount_line = lines[j + 1].strip()
                            discount_match = re.match(discount_pattern, discount_line)
                            if discount_match:
                                discount = float(discount_match.group(1))
                                j += 1  # Skip discount line
                        
                        break
                    else:
                        # Add this line to item name if it doesn't contain totals
                        if not re.search(r'(SUBTOTAL|TAX|TOTAL)', next_line, re.IGNORECASE):
                            item_name += " " + next_line
                    j += 1
                
                if price > 0:
                    items.append({
                        'item_code': item_code,
                        'item_name': item_name.strip(),
                        'price': price,
                        'discount': discount
                    })
                
                i = j
                continue
            
            i += 1
        
        return {
            'items': items,
            'subtotal': subtotal,
            'tax': tax,
            'total': total
        }
    except Exception as e:
        logging.error(f"Error parsing receipt: {e}")
        return None

@app.route('/')
def index():
    """Main page showing upload form and receipt history"""
    receipts_data = load_receipts_data()
    return render_template('index.html', receipts=receipts_data)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle PDF upload and processing"""
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    if not allowed_file(file.filename):
        flash('Only PDF files are allowed', 'error')
        return redirect(url_for('index'))
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Extract text from PDF
        text = extract_text_from_pdf(filepath)
        if not text:
            flash('Failed to extract text from PDF', 'error')
            return redirect(url_for('index'))
        
        # Parse receipt data
        parsed_data = parse_costco_receipt(text)
        if not parsed_data or not parsed_data['items']:
            flash('Failed to parse receipt data. Please ensure this is a valid Costco receipt.', 'error')
            return redirect(url_for('index'))
        
        # Load existing data and append new receipt
        receipts_data = load_receipts_data()
        
        new_receipt = {
            'id': len(receipts_data) + 1,
            'filename': file.filename,
            'upload_date': datetime.now().isoformat(),
            'items': parsed_data['items'],
            'subtotal': parsed_data['subtotal'],
            'tax': parsed_data['tax'],
            'total': parsed_data['total']
        }
        
        receipts_data.append(new_receipt)
        
        # Save updated data
        if save_receipts_data(receipts_data):
            flash(f'Receipt processed successfully! Found {len(parsed_data["items"])} items.', 'success')
        else:
            flash('Receipt processed but failed to save data', 'warning')
        
        # Clean up uploaded file
        try:
            os.remove(filepath)
        except:
            pass
            
    except Exception as e:
        logging.error(f"Error processing upload: {e}")
        flash('An error occurred while processing the file', 'error')
    
    return redirect(url_for('index'))

@app.route('/clear_data', methods=['POST'])
def clear_data():
    """Clear all receipt data"""
    try:
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        flash('All receipt data cleared successfully', 'success')
    except Exception as e:
        logging.error(f"Error clearing data: {e}")
        flash('Error clearing data', 'error')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
