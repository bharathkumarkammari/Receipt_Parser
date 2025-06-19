import os
import json
import re
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import pdfplumber
from werkzeug.utils import secure_filename
import gspread
from google.oauth2.service_account import Credentials
from PIL import Image
import pytesseract

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "fallback_secret_key_for_development")

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
DATA_FILE = 'receipts_data.json'

# Create upload directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Set tesseract_cmd if needed (update the path if your tesseract is elsewhere)
pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'

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

def extract_text_from_image(image_path):
    """Extract text from an image using pytesseract."""
    try:
        img = Image.open(image_path)
        img = img.convert('RGB')  # Convert to standard RGB
        text = pytesseract.image_to_string(img)
        print(f"OCR TEXT: {text}")  # Debug print
        return text
    except Exception as e:
        logging.error(f"Error extracting text from image: {e}")
        return None

def combine_multiline_items(lines):
    """Combine multi-line items into a single line using item code as the base, skipping metadata and member numbers."""
    combined = []
    buffer = ''
    # Item code pattern: E or F (optional) followed by digits
    item_code_pattern = re.compile(r'^(E|F)?\s*\d+')
    # Metadata patterns (member, subtotal, tax, total, etc.)
    metadata_patterns = [
        re.compile(r'^Member', re.IGNORECASE),
        re.compile(r'^KING OF PRUSSIA', re.IGNORECASE),
        re.compile(r'^\d{10,}$'),  # long numbers (member numbers, etc.)
        re.compile(r'SUBTOTAL', re.IGNORECASE),
        re.compile(r'TAX', re.IGNORECASE),
        re.compile(r'TOTAL', re.IGNORECASE),
        re.compile(r'AMOUNT', re.IGNORECASE),
        re.compile(r'CHANGE', re.IGNORECASE),
        re.compile(r'ITEMS SOLD', re.IGNORECASE),
        re.compile(r'INSTANT SAVINGS', re.IGNORECASE),
        re.compile(r'^https?://', re.IGNORECASE),
    ]
    for line in lines:
        # If this is a new item line
        if item_code_pattern.match(line):
            if buffer:
                combined.append(buffer.strip())
            buffer = line
        # If this is a metadata or member line, skip it
        elif any(pat.search(line) for pat in metadata_patterns):
            continue
        # If this is a line of just digits (likely metadata), skip it
        elif line.isdigit():
            continue
        # Otherwise, append to the current item buffer
        else:
            buffer += ' ' + line
    if buffer:
        combined.append(buffer.strip())
    return combined

def parse_costco_receipt(text):
    """Parse Costco receipt text to extract items, prices, totals, and date"""
    try:
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        items = []
        subtotal = None
        tax = None
        total = None
        # Extract date (MM/DD/YYYY)
        date_pattern = r'(\d{2}/\d{2}/\d{4})'
        date_match = re.search(date_pattern, text)
        receipt_date = date_match.group(1) if date_match else None
        # Regex patterns for Costco receipts - updated for all item formats
        subtotal_pattern = r'SUBTOTAL\s+(\d+\.\d{2})'
        tax_pattern = r'TAX\s+(\d+\.\d{2})'
        total_pattern = r'\*+\s*TOTAL\s+(\d+\.\d{2})'
        
        # Pattern for item lines: E or F or just code, name, price, and tax indicator
        item_pattern = r'(?:[EF]\s+)?(\d+)\s+(.+?)\s+(\d+\.\d{2})\s+[NY]'
        
        # Pattern for partial item lines (item code only with price on next line)
        partial_item_pattern = r'(?:[EF]\s+)?(\d+)\s+(\d+\.\d{2})\s+[NY]'
        
        # Pattern for discount lines: item code / original code followed by discount amount
        discount_pattern = r'(\d+)\s*/\s*(\d+)\s+(\d+\.\d{2})-'
        
        # Pattern for non-food items (taxable): item code, name, price, Y
        taxable_item_pattern = r'^(\d+)\s+(.+?)\s+(\d+\.\d{2})\s+Y'
        
        # Store discounts to apply later
        discounts = {}
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
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
            
            # Check for discount lines (e.g., 345771 /1792879 6.00-)
            discount_match = re.match(discount_pattern, line)
            if discount_match:
                discount_code = discount_match.group(2)  # The original item code
                discount_amount = float(discount_match.group(3))
                discounts[discount_code] = discount_amount
                i += 1
                continue
            
            # Check for food items (starting with E or F) - complete line with name and price
            item_match = re.match(item_pattern, line)
            if item_match:
                item_code = item_match.group(1)
                item_name = item_match.group(2).strip()
                price = float(item_match.group(3))
                items.append({
                    'item_code': item_code,
                    'item_name': item_name,
                    'price': price
                })
                i += 1
                continue
            
            # Check for partial item lines (item code with price, but name on previous lines)
            partial_match = re.match(partial_item_pattern, line)
            if partial_match:
                item_code = partial_match.group(1)
                price = float(partial_match.group(2))
                # Look backwards for the item name
                item_name_parts = []
                j = i - 1
                while j >= 0 and j > i - 5:  # Look back up to 5 lines
                    prev_line = lines[j]
                    # Stop if we hit another item line or receipt metadata
                    if (re.match(r'[EF]\s+\d+', prev_line) or 
                        re.match(r'Member|KING OF PRUSSIA|^\d{20}', prev_line) or
                        'SUBTOTAL' in prev_line or 'TAX' in prev_line or 'TOTAL' in prev_line):
                        break
                    # Skip lines that are just single words or numbers
                    if len(prev_line.split()) >= 1 and not prev_line.isdigit():
                        item_name_parts.insert(0, prev_line)
                    j -= 1
                item_name = ' '.join(item_name_parts) if item_name_parts else f"ITEM {item_code}"
                items.append({
                    'item_code': item_code,
                    'item_name': item_name.strip(),
                    'price': price
                })
                i += 1
                continue
            
            # Check for taxable items (no E or F prefix)
            taxable_match = re.match(taxable_item_pattern, line)
            if taxable_match:
                item_code = taxable_match.group(1)
                item_name = taxable_match.group(2).strip()
                price = float(taxable_match.group(3))
                items.append({
                    'item_code': item_code,
                    'item_name': item_name,
                    'price': price
                })
                i += 1
                continue
            
            i += 1
        
        # Apply discounts to items after all items are parsed
        for item in items:
            code = item['item_code']
            discount = discounts.get(code, 0.0)
            item['discount'] = discount
            item['final_price'] = item['price'] - discount
        
        # Calculate totals for validation
        calculated_subtotal = sum(item['final_price'] for item in items)
        total_discounts = sum(item['discount'] for item in items)
        calculated_total = calculated_subtotal + (tax or 0)
        
        # Validation flags
        subtotal_valid = abs(calculated_subtotal - (subtotal or 0)) < 0.01 if subtotal else None
        total_valid = abs(calculated_total - (total or 0)) < 0.01 if total else None
        
        return {
            'items': items,
            'subtotal': subtotal,
            'tax': tax,
            'total': total,
            'calculated_subtotal': calculated_subtotal,
            'calculated_total': calculated_total,
            'total_discounts': total_discounts,
            'subtotal_valid': subtotal_valid,
            'total_valid': total_valid,
            'receipt_date': receipt_date
        }
    except Exception as e:
        logging.error(f"Error parsing receipt: {e}")
        return None

@app.route('/')
def index():
    """Main page showing upload form and receipt history"""
    receipts_data = load_receipts_data()
    tableau_url = "https://public.tableau.com/views/ReceiptDashboard/Dashboard?:showVizHome=no&:embed=true"
    return render_template('index.html', receipts=receipts_data, tableau_url=tableau_url)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle PDF or image upload and processing"""
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    if not file.filename or not allowed_file(file.filename):
        flash('Only PDF or image files are allowed', 'error')
        return redirect(url_for('index'))
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Extract text based on file type
        ext = filename.rsplit('.', 1)[1].lower()
        if ext == 'pdf':
            text = extract_text_from_pdf(filepath)
        elif ext in {'jpg', 'jpeg', 'png'}:
            text = extract_text_from_image(filepath)
        else:
            flash('Unsupported file type.', 'error')
            return redirect(url_for('index'))
        
        if not text:
            flash('Failed to extract text from file', 'error')
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
            'total': parsed_data['total'],
            'calculated_subtotal': parsed_data['calculated_subtotal'],
            'calculated_total': parsed_data['calculated_total'],
            'total_discounts': parsed_data['total_discounts'],
            'subtotal_valid': parsed_data['subtotal_valid'],
            'total_valid': parsed_data['total_valid'],
            'receipt_date': parsed_data['receipt_date']
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

@app.route('/upload_to_gsheet', methods=['POST'])
def upload_to_gsheet():
    """Upload the latest parsed receipt to Google Sheets, including date column"""
    try:
        receipts_data = load_receipts_data()
        if not receipts_data:
            flash('No receipts to upload.', 'error')
            return redirect(url_for('index'))
        latest = receipts_data[-1]
        items = latest.get('items', [])
        # Google Sheets setup
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file('service_account.json', scopes=scope)
        client = gspread.authorize(creds)
        # Open the sheet (replace with your sheet name)
        sheet = client.open("Costco_Input").sheet1
        # Add 'Date' to header if not present
        header = ["Item Code", "Item Name", "Price", "Discount", "Final Price", "Date"]
        if len(sheet.get_all_values()) == 0:
            sheet.append_row(header)
        # For each item, add a row with the date
        for item in items:
            row = [
                item['item_code'],
                item['item_name'],
                item['price'],
                item.get('discount', ''),
                item.get('final_price', ''),
                latest.get('receipt_date')
            ]
            sheet.append_row(row)
        flash('Latest receipt uploaded to Google Sheets!', 'success')
    except Exception as e:
        logging.error(f"Error uploading to Google Sheets: {e}")
        flash('Failed to upload to Google Sheets. Check server logs and credentials.', 'error')
    return redirect(url_for('index'))

@app.route('/delete_receipt/<receipt_id>', methods=['POST'])
def delete_receipt(receipt_id):
    """Delete a specific receipt by its ID"""
    try:
        receipts = load_receipts_data()
        # Convert receipt_id to integer for comparison
        receipt_id = int(receipt_id)
        # Find and remove the receipt with the matching ID
        receipts = [r for r in receipts if r.get('id') != receipt_id]
        if save_receipts_data(receipts):
            flash('Receipt deleted successfully', 'success')
        else:
            flash('Error deleting receipt', 'error')
    except Exception as e:
        logging.error(f"Error deleting receipt: {e}")
        flash('Error deleting receipt', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
