# 🌾 Vikaspedia Farmer Scheme PDF Downloader

A beginner-friendly web scraping application built with
**Python, Playwright and Streamlit**.

The application allows a user to:

- Enter a webpage URL
- Open the webpage using Playwright
- Discover possible PDF/document links
- Select documents using checkboxes
- Download individual documents
- Download selected documents
- Download all discovered documents
- View download progress
- Automatically retry failed downloads
- Handle errors gracefully

---

# 📁 Project Structure

```text
vikaspedia-scraper/
│
├── .venv/
│
├── app.py
│
├── scraper/
│   ├── __init__.py
│   ├── vikaspedia.py
│   └── downloader.py
│
├── downloads/
│
├── tests/
│   └── test_scraper.py
│
├── requirements.txt
│
├── .gitignore
│
└── README.md