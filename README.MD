# Vikaspedia Farmer Schemes PDF Scraper

A Python + Playwright + Streamlit application that discovers Farmer Schemes from Vikaspedia, handles pagination, opens each individual scheme page, and downloads the scheme PDF.

## 1. Workflow

```text
Vikaspedia Farmer Schemes
        |
        v
Detect Pagination
        |
        v
Pages 1 ... N
        |
        v
Extract Scheme Names
        |
        v
Click Scheme Card
        |
        v
Individual Scheme Page
        |
        v
Download as PDF
        |
        v
downloads/*.pdf
```

The currently tested Vikaspedia page exposes 5 pagination pages and the tests identified 27 actual schemes. UI items such as `Lets Connect`, `Let's Connect`, and `menu` are filtered out.

## 2. Technology Stack

- **Python** - application language
- **Playwright** - browser automation and PDF download
- **Chromium** - browser used by Playwright
- **Streamlit** - web interface
- **Pytest** - testing framework

## 3. Project Structure

```text
vikaspedia-scraper/
|
|-- .venv/
|-- app.py
|
|-- scraper/
|   |-- __init__.py
|   |-- vikaspedia.py
|   `-- downloader.py
|
|-- downloads/
|   |-- .gitkeep
|   `-- *.pdf
|
|-- tests/
|   |-- test_pagination.py
|   `-- test_pdf_download.py
|
|-- requirements.txt
|-- .gitignore
`-- README.md
```

### File responsibilities

| File | Purpose |
|---|---|
| `app.py` | Streamlit UI |
| `scraper/vikaspedia.py` | Pagination, scheme extraction and individual URL discovery |
| `scraper/downloader.py` | PDF download and retry logic |
| `scraper/__init__.py` | Python package initialization |
| `tests/test_pagination.py` | Pagination and scheme extraction test |
| `tests/test_pdf_download.py` | PDF download test |
| `requirements.txt` | Dependencies |
| `.gitignore` | Files excluded from Git |
| `downloads/` | Local PDF output |

## 4. Prerequisites

Recommended environment:

- Windows 10/11
- Python 3.10+
- Visual Studio Code
- Internet connection
- Git (optional)

## 5. Create the Virtual Environment

From the project directory:

```bat
python -m venv .venv
```

Activate it in Windows CMD:

```bat
.venv\Scripts\activate
```

PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

You should see `(.venv)` in the terminal.

## 6. Install Dependencies

```bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Install the Playwright Chromium browser:

```bat
playwright install chromium
```

Verify:

```bat
playwright --version
```

## 7. Vikaspedia URL

Default URL:

```text
https://schemes.vikaspedia.in/viewcontent/schemesall/schemes-for-farmers?lgn=en
```

The same URL is pre-filled in the Streamlit application, but the user can provide a URL through the UI.

## 8. Why Two-Level Navigation Is Needed

The scheme listing does not expose every PDF as a direct PDF link.

The application therefore follows:

```text
Listing Page
    |
    +--> Scheme Card
            |
            v
       Individual Scheme
            |
            +--> Download as PDF
                    |
                    v
                   PDF
```

For example, clicking `Pradhan Mantri Kisan Samman Nidhi` opens its individual Vikaspedia page. The PDF is then downloaded from that page.

## 9. Important HTML Discovery

The site uses a React/Material UI interface.

The visible scheme name may be truncated:

```text
Pradhan Mantri Kisan Samman Ni...
```

The full name is stored in the HTML `title` attribute:

```html
<h6 title="Pradhan Mantri Kisan Samman Nidhi">
```

Therefore the scraper uses:

```css
h6[title]
```

and reads the `title` attribute.

The scheme card itself does not necessarily contain an ordinary `href`. The scraper finds the `h6[title]` and its nearest ancestor `div[@title]`, then clicks that Material UI card.

## 10. Pagination

The scraper detects visible numeric controls rather than permanently hard-coding page numbers.

The current test detected:

```text
1 2 3 4 5
```

The scraper processes each detected page and extracts its schemes.

## 11. Non-Scheme Filtering

The generic `h6[title]` selector also finds some UI elements.

These are excluded:

```python
EXCLUDED_TITLES = {
    "Lets Connect",
    "Let's Connect",
    "menu",
}
```

This produced 27 actual schemes in the successful pagination test.

The live website can change, so the actual count should always be determined by running the scraper.

## 12. Test Pagination and Scheme Extraction

Run:

```bat
python tests\test_pagination.py
```

Expected important output:

```text
VISIBLE NUMERIC PAGINATION CONTROLS: [1, 2, 3, 4, 5]

PAGE 1 - ...
PAGE 2 - ...
PAGE 3 - ...
PAGE 4 - ...
PAGE 5 - ...

TOTAL UNIQUE SCHEMES FOUND: 27
```

The browser is intentionally visible in this standalone test so that Playwright activity can be observed.

## 13. Test PDF Download

Run:

```bat
python tests\test_pdf_download.py
```

The test uses the confirmed individual scheme URL for:

```text
Pradhan Mantri Kisan Samman Nidhi
```

It locates:

```html
<button title="Download as PDF">
```

and captures the browser download.

A successful test creates:

```text
downloads/
`-- Pradhan_Mantri_Kisan_Samman_Nidhi.pdf
```

The test verifies that the file exists and has a non-zero size.

## 14. Retry Logic

The PDF downloader uses three attempts by default:

```text
Attempt 1
   |
   X
   |
Retry
   |
Attempt 2
   |
   X
   |
Retry
   |
Attempt 3
```

If all attempts fail, the application reports the error instead of silently ignoring it.

## 15. Filename Handling

Windows does not allow certain characters in filenames.

The downloader replaces unsafe characters such as:

```text
< > : " / \ | ? *
```

with `_`.

Whitespace is also normalized.

Example:

```text
Pradhan Mantri Kisan Samman Nidhi
```

becomes:

```text
Pradhan_Mantri_Kisan_Samman_Nidhi.pdf
```

## 16. Run the Streamlit Application

After the two standalone tests pass:

```bat
streamlit run app.py
```

Streamlit will display a local address in the terminal. Open that address in your browser.

## 17. Streamlit Features

The application provides:

### URL input

Enter the Farmer Schemes listing URL.

### Scan All Schemes

The application starts Playwright and discovers:

- pagination pages
- scheme names
- individual scheme URLs

### Select All

Select all discovered schemes.

### Individual Download

Each scheme has its own Download button.

### Download Selected

Download only the checked schemes.

### Download All

Download every discovered scheme.

### Progress Bar

Bulk downloads display progress.

### Retry

Each PDF gets multiple attempts.

### Error Handling

Failed downloads are reported without stopping the complete batch.

## 18. Recommended Testing Order

Do not immediately start with Download All.

Use this order:

### Step 1

```bat
python tests\test_pagination.py
```

Confirm that pagination and schemes are detected.

### Step 2

```bat
python tests\test_pdf_download.py
```

Confirm that a PDF is created.

### Step 3

```bat
streamlit run app.py
```

Click:

```text
Scan All Schemes
```

### Step 4

Download one scheme.

### Step 5

Select 2-3 schemes and click:

```text
Download Selected
```

### Step 6

After the smaller test succeeds, click:

```text
Download All
```

## 19. Download Directory

All PDFs are saved to:

```text
downloads/
```

Example:

```text
downloads/
|-- Agriculture_Infrastructure_Fund.pdf
|-- Crop_insurance_schemes.pdf
|-- Krishi_UDAN_scheme.pdf
|-- National_Mission_on_Natural_Farming.pdf
`-- Pradhan_Mantri_Kisan_Samman_Nidhi.pdf
```

Downloaded PDFs are excluded from Git using:

```text
downloads/*.pdf
```

This keeps the repository focused on source code rather than generated documents.

## 20. Architecture

```text
                    User
                     |
                     v
              +-------------+
              |  Streamlit  |
              |    app.py   |
              +------+------+
                     |
          +----------+----------+
          |                     |
          v                     v
+-------------------+   +-------------------+
| VikaspediaScraper |   |  PDFDownloader    |
| vikaspedia.py     |   |  downloader.py    |
+---------+---------+   +---------+---------+
          |                       |
          v                       v
 Pagination + URLs        Download as PDF
          |                       |
          +-----------+-----------+
                      |
                      v
                downloads/*.pdf
```

## 21. Why Responsibilities Are Separated

`app.py` is responsible for the UI.

`vikaspedia.py` is responsible for finding schemes and their individual pages.

`downloader.py` is responsible for downloading PDFs.

This makes the project easier to debug and extend.

For example, the PDF downloader can later be reused by another application without copying the Streamlit code.

## 22. Future RAG Integration

The downloaded PDFs are intended to become the document source for a future RAG application.

Planned pipeline:

```text
Vikaspedia
    |
    v
Playwright Scraper
    |
    v
Scheme PDFs
    |
    v
PDF Text Extraction
    |
    v
Document Chunking
    |
    v
Embeddings
    |
    v
Vector Database
    |
    v
Retriever
    |
    v
LLM
    |
    v
Question + Answer
```

Example future question:

```text
What are the eligibility requirements for Pradhan Mantri Kisan Samman Nidhi?
```

The RAG system would retrieve relevant content from the downloaded scheme documents and use that context to generate an answer.

## 23. Possible Future RAG Structure

```text
vikaspedia-rag/
|
|-- app.py
|
|-- scraper/
|   |-- vikaspedia.py
|   `-- downloader.py
|
|-- documents/
|   `-- *.pdf
|
|-- ingestion/
|   |-- pdf_loader.py
|   |-- chunker.py
|   `-- embeddings.py
|
|-- vectorstore/
|
|-- rag/
|   |-- retriever.py
|   `-- qa.py
|
`-- tests/
```

## 24. Git Setup

If using Git:

```bat
git init
```

Configure identity if needed:

```bat
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

Check:

```bat
git status
```

Add source files:

```bat
git add .
```

Commit:

```bat
git commit -m "Build Vikaspedia farmer schemes scraper"
```

If a GitHub repository already exists:

```bat
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

## 25. Git Security

Never commit:

```text
.env
API keys
passwords
access tokens
private credentials
```

If future RAG code uses an API key, keep it in environment variables and add `.env` to `.gitignore`.

## 26. Stop Streamlit

In the terminal running Streamlit:

```text
Ctrl + C
```

## 27. Troubleshooting

### Playwright browser missing

Run:

```bat
playwright install chromium
```

### Playwright module missing

Activate the virtual environment:

```bat
.venv\Scripts\activate
```

Then:

```bat
pip install -r requirements.txt
```

### Streamlit module missing

```bat
pip install streamlit
```

### No schemes found

Check:

1. Internet connection.
2. Vikaspedia URL opens manually.
3. `test_pagination.py` works.
4. The website has not changed its HTML structure.

The current scraper waits for:

```css
h6[title]
```

because the site renders its content dynamically.

### PDF timeout

Possible causes:

- Slow connection
- Temporary website response problem
- Website structure change
- Browser timeout

The downloader automatically retries.

### Scan is slow

This is expected because every scheme requires navigation from the listing page to the individual scheme page to discover its URL.

For approximately 27 schemes:

```text
Listing
  -> Scheme 1
  -> Listing
  -> Scheme 2
  -> Listing
  ...
```

## 28. Current Project Status

```text
[✓] Python environment
[✓] Playwright
[✓] Chromium
[✓] Vikaspedia listing page
[✓] Pagination detection
[✓] Scheme extraction
[✓] Non-scheme filtering
[✓] Scheme card navigation
[✓] Individual scheme URL discovery
[✓] Download as PDF detection
[✓] PDF download
[✓] Retry handling
[✓] Streamlit interface
[✓] Individual download
[✓] Selected download
[✓] Download all
[✓] Progress bar
[✓] Error handling
[ ] PDF text extraction
[ ] Chunking
[ ] Embeddings
[ ] Vector database
[ ] RAG question answering
```

## 29. Quick Start

Fresh Windows setup:

```bat
cd vikaspedia-scraper
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

Test pagination:

```bat
python tests\test_pagination.py
```

Test PDF:

```bat
python tests\test_pdf_download.py
```

Start application:

```bat
streamlit run app.py
```

## 30. Final End-to-End Design

```text
                  VIKASPEDIA
                       |
                       v
              Farmer Schemes Page
                       |
                       v
                 Pagination
                       |
          +------------+------------+
          |            |            |
        Page 1       Page 2       Page N
          |            |            |
          +------------+------------+
                       |
                       v
                 Scheme Cards
                       |
                       v
              Individual Scheme
                       |
                       v
               Download as PDF
                       |
                       v
                  Local PDFs
                       |
                       v
              Future RAG Pipeline
                       |
          +------------+------------+
          |            |            |
       Extract       Chunk       Embed
          |            |            |
          +------------+------------+
                       |
                       v
                 Vector Store
                       |
                       v
                   Retriever
                       |
                       v
                     LLM
                       |
                       v
                  User Answer
```

## 31. Important Maintenance Note

This project relies on the current HTML structure and browser behavior of Vikaspedia.

If Vikaspedia changes:

- CSS/HTML structure
- pagination implementation
- scheme-card structure
- PDF button
- navigation behavior

the Playwright selectors may need to be updated.

The two standalone tests should therefore be run after major website changes before relying on the complete Streamlit application.

## 32. Project Goal

The immediate goal is reliable automated collection of Vikaspedia Farmer Scheme PDFs.

The larger goal is to use those documents as a controlled knowledge source for a RAG application capable of answering questions about farmer schemes using retrieved document content.
