# ReceiptViz 🧾 – Costco Receipt Parser & Analytics Dashboard

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Visit-green?style=for-the-badge)](https://receiptviz.onrender.com)
[![Portfolio](https://img.shields.io/badge/Author-Portfolio-blue?style=for-the-badge)](https://bharathkumarkammari.com)

---

## 🚀 What is ReceiptViz?

**ReceiptViz** is a smart web application that lets you upload your Costco receipts (PDF or image), automatically extracts all items, discounts, and totals, and syncs your purchase history to Google Sheets.  
It features a beautiful dashboard powered by **Power BI**, giving you real-time analytics on your spending, savings, and itemized history.

---

## ✨ Features

- **Upload Costco Receipts** (PDF, JPG, PNG)
- **Automatic Parsing**: Extracts item names, prices, discounts, and dates
- **Google Sheets Sync**: All data is stored and updated live in your Google Sheet
- **Power BI Dashboard**: Embedded analytics dashboard for instant insights
- **Real-Time Data**: Dashboard refreshes up to **8 times/day** (free Power BI account limit)
- **Accordion Receipt History**: Visual, expandable list of all your receipts
- **Validation**: Green checkmark if items match the receipt total
- **Modern UI**: Responsive, dark-themed, and mobile-friendly

---

## 🖥️ Live Demo

👉 **Try it now:** [https://receiptviz.onrender.com](https://receiptviz.onrender.com)

---

## 📊 Power BI Integration

- The dashboard is embedded using Power BI's **Publish to Web** feature.
- **Real-time data**: The dashboard fetches the latest data from Google Sheets every time you refresh (up to 8 times/day for free accounts, 48 for Premium).
- **No login required**: Anyone can view the analytics instantly.

---

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, Bootstrap, JavaScript
- **PDF/Image Parsing**: pdfplumber, pytesseract
- **Data Store**: Google Sheets (via Service Account)
- **Analytics**: Power BI (embedded)
- **Hosting**: Render.com

---

## 📂 Project Structure

```
Receipt_Parser/
├── app.py                 # Main Flask app
├── main.py                # Entrypoint for deployment
├── templates/             # HTML templates (Jinja2)
├── static/                # CSS, JS, and assets
├── uploads/               # Uploaded receipts (temp)
├── receipts_data.json     # Local cache (optional)
├── requirements.txt       # Python dependencies
├── render.yaml            # Render deployment config
├── DEPLOYMENT_NOTES.md    # Deployment & environment setup
└── README.md
```

---

## ⚡ How It Works

1. **Upload** your Costco receipt (PDF or image)
2. The app **extracts** all items, discounts, and totals
3. Data is **synced to Google Sheets** (your source of truth)
4. The **Power BI dashboard** fetches the latest data from Google Sheets
5. View your **analytics** and **receipt history** instantly

---

## 📝 Setup & Deployment

See [`DEPLOYMENT_NOTES.md`](./DEPLOYMENT_NOTES.md) for full instructions.

**Key steps:**
- Set up a Google Cloud Service Account and share your Google Sheet
- Set all required environment variables (see deployment notes)
- Deploy to [Render.com](https://render.com) or your preferred cloud

---

## 🔒 Security & Privacy

- Your receipts are processed in-memory and synced to your private Google Sheet
- No data is stored on the server after upload
- Service account credentials are never committed to the repo

---

## 💡 Customization Ideas

- Add category auto-tagging for items
- Export analytics as PDF or image
- Connect to other BI tools (Tableau, Power BI Premium, etc.)

---

## 👤 Author

Made with ❤️ by [Bharath Kumar Kammari](https://bharathkumarkammari.com)

---

## 📢 License

Free for personal and demo use.  
For commercial or enterprise use, please contact the author.
