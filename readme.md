# ReceiptViz 🧾 – Costco Receipt Parser & Visualizer

A smart web application that extracts items, discounts, and tax details from Costco PDF receipts, then transforms them into structured data and visuals. Perfect for personal expense tracking and dashboarding.

🔗 **Live App**: [https://receiptviz.onrender.com](https://receiptviz.onrender.com)  
📂 **GitHub Repo**: [Receipt_Parser (receipt_parse branch)](https://github.com/bharathkumarkammari/Receipt_Parser/tree/receipt_parse)

---

## 🔍 Features

- Upload your **Costco PDF receipt**
- Automatically extracts:
  - 🛒 Item names
  - 💸 Discounts
  - 🧾 Taxes
  - 🗓️ Purchase date
- Detects and links discounts even if they’re on a different line
- Outputs:
  - Cleaned structured data
  - Preprocessed summary
  - Optional download of results
- Ready to connect to Tableau or Google Sheets for dashboards

---

## ⚙️ Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML/CSS, Bootstrap, JavaScript
- **PDF Parsing**: `pdfplumber`, `pdfminer.six`
- **Hosting**: Render.com

---

## 📂 File Structure

```
Receipt_Parser/
├── app.py                 # Core Flask app
├── main.py                # Upload and route manager
├── tableau_api.py         # (Optional) for Tableau extensions
├── templates/             # HTML templates
├── static/                # CSS and JS
├── uploads/               # Uploaded receipts
├── receipts_data.json     # Parsed receipt storage
├── requirements.txt
└── render.yaml            # Render deployment config
```

---

## 🚀 How to Deploy (Render)

1. Connect this repo to [Render.com](https://render.com)
2. Add `render.yaml` and set:
   ```yaml
   startCommand: gunicorn main:app
   ```
3. App will be live at:
   ```
   https://yourname.onrender.com
   ```

---

## ✅ Future Ideas

- Auto-categorize expenses (e.g., grocery, electronics)
- Monthly or weekly spending summary
- Connect to Google Sheets / Airtable
- Dashboard export as PDF or image

---

## 📝 License

Free for personal and demo use. Created by [bharathkumarkammari.com](https://bharathkumarkammari.com)
