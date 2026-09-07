# Vikaspedia Agri Farmer Adviser --- Self-RAG Chatbot

## 1. Project Overview

The **Vikaspedia Agri Farmer Adviser** is a beginner-friendly GenAI
application that answers Indian agriculture and farmer-support questions
using a curated collection of Vikaspedia scheme PDFs.

The application combines:

-   Playwright browser automation for PDF discovery/download
-   PyMuPDF for PDF text extraction
-   Tesseract OCR for scanned/image PDFs
-   Text chunking and OpenAI embeddings
-   FAISS vector search
-   RAG-based answer generation
-   Self-RAG routing
-   Low-request optimization
-   Serper live web-search fallback
-   PDF and web source citations
-   Safe error handling
-   Retrieval evaluation
-   LangSmith monitoring
-   Streamlit customer and Developer Version interfaces

The current frozen scope contains 11 features:

    \# Feature                    Status
  ---- -------------------------- --------------------------
     1 PDF Scraper                PASS
     2 OCR Processing             PASS
     3 FAISS Vector Database      PASS
     4 RAG Chatbot                PASS
     5 Self-RAG                   PASS
     6 Low-Request Optimization   PASS
    11 PDF Source Citations       PASS
    12 Web Search Fallback        PASS
    14 Error Handling             PASS
    15 Evaluation Framework       PASS --- Retrieval 10/10
    16 LangSmith Monitoring       PASS

------------------------------------------------------------------------

# 2. What Problem Does This Project Solve?

Farmers may ask:

-   What is PM-KISAN?
-   What benefits are available under crop insurance?
-   What support is available for irrigation?
-   What subsidies are available?
-   What agriculture schemes are available?
-   What are the latest farmer scheme updates?

A normal LLM alone is not ideal because it may not know the
application's curated documents or may not have current information.

This project uses **RAG** to ground answers in retrieved documents and
**web fallback** for current information.

The simplest mental model is:

``` text
User Question
      |
      v
Is it agriculture related?
      |
      +---- NO ----> Friendly out-of-scope response
      |
     YES
      |
      v
Can the PDF knowledge base answer it?
      |
      +---- YES ---> FAISS ---> PDF context ---> LLM
      |
      +---- NO ----> Serper ---> Web context ---> LLM
                                      |
                                      v
                              Answer + Sources
```

------------------------------------------------------------------------

# 3. Architecture

``` text
                         +----------------------+
                         |      Streamlit UI    |
                         |    app_adviser.py    |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         |       Self-RAG        |
                         |    rag/self_rag.py   |
                         +----------+-----------+
                                    |
                       +------------+------------+
                       |                         |
                       v                         v
                 Scope / Routing          Retrieval / Freshness
                       |                         |
             +---------+---------+       +-------+-------+
             |                   |       |               |
          Out of Scope         Valid  Strong PDF      Weak/current
             |                   |       |               |
             v                   v       v               v
          Message             FAISS    LLM            Serper
                                     \                   /
                                      \                 /
                                       +-------+-------+
                                               |
                                               v
                                         OpenAI LLM
                                               |
                                               v
                                      Answer + Citations
                                               |
                                               v
                                          LangSmith
```

------------------------------------------------------------------------

# 4. End-to-End Data Flow

## 4.1 Knowledge-building flow

``` text
Vikaspedia Farmer Schemes
          |
          v
      Playwright
          |
          v
       PDF files
          |
          v
    PyMuPDF extraction
          |
          +---- enough text ----> extracted text
          |
          +---- scanned PDF ----> Tesseract OCR
                                      |
                                      v
                                  extracted text
                                      |
                                      v
                                  Text chunks
                                      |
                                      v
                            OpenAI embeddings
                                      |
                                      v
                                   FAISS
```

## 4.2 Question-answering flow

``` text
User question
      |
      v
Scope check
      |
      +---- unrelated ----> OUT_OF_SCOPE
      |
      v
Self-RAG decision
      |
      +---- reliable PDF evidence ----> Generate from PDF
      |
      +---- current/weak evidence ----> Serper web search
                                            |
                                            v
                                     Generate from web
                                            |
                                            v
                                  Answer + source list
```

------------------------------------------------------------------------

# 5. Technology Stack

## Python

Main programming language.

Why:

-   Easy for beginners
-   Strong AI ecosystem
-   Excellent automation libraries
-   Easy integration with Streamlit and LangChain

## Streamlit

Provides the web application UI.

Run:

``` cmd
streamlit run app_adviser.py
```

## Playwright

Automates the Vikaspedia website.

It handles:

1.  Opening the Farmer Schemes page
2.  Pagination
3.  Scheme-card discovery
4.  Opening scheme pages
5.  Clicking Download as PDF
6.  Capturing downloads
7.  Saving PDFs locally

## PyMuPDF

Reads PDF pages and attempts normal text extraction.

## Tesseract OCR

Handles scanned/image-based PDF pages when normal extraction produces
insufficient text.

Windows installation:

``` cmd
winget install UB-Mannheim.TesseractOCR
```

Verification:

``` cmd
"C:\Program Files\Tesseract-OCR\tesseract.exe" --version
```

## FAISS

Local vector similarity search engine.

It allows semantic search instead of relying only on exact keywords.

## OpenAI Embeddings

The validated embedding model is:

``` text
text-embedding-3-small
```

It converts document chunks and questions into vectors.

## OpenAI LLM

The validated generation model is:

``` text
gpt-4.1-mini
```

The LLM generates the final grounded response.

## LangChain / LangGraph

LangChain integrates the LLM/retrieval components.

LangGraph represents the Self-RAG decision flow as explicit nodes.

## Serper

Provides live Google search for the web fallback.

Environment variable:

``` env
SERPER_API_KEY=your-serper-key
```

## LangSmith

Provides observability for LangGraph and LLM execution.

It captures:

-   Nodes
-   Inputs/outputs
-   Latency
-   Token usage
-   Cost
-   Tags
-   Metadata

------------------------------------------------------------------------

# 6. RAG Explained for Beginners

RAG means **Retrieval-Augmented Generation**.

Without RAG:

``` text
Question ---> LLM ---> Answer
```

With RAG:

``` text
Question
   |
   v
Search knowledge base
   |
   v
Relevant evidence
   |
   v
LLM + evidence
   |
   v
Answer
```

The important idea is that the LLM is given relevant application data
before generating the answer.

This reduces the risk of answering from unsupported knowledge.

------------------------------------------------------------------------

# 7. Embeddings and FAISS Explained

An embedding converts text into a numerical vector representing semantic
meaning.

For example:

``` text
"crop insurance benefits"
          |
          v
     embedding vector
```

A question is embedded in the same way.

FAISS compares the question vector with document vectors and retrieves
similar chunks.

``` text
Question vector
       |
       v
     FAISS
       |
       +--> Chunk A
       +--> Chunk B
       +--> Chunk C
```

This is why a question such as:

``` text
"What financial protection do farmers get for crop loss?"
```

can retrieve information from a document discussing crop insurance even
when the wording is different.

------------------------------------------------------------------------

# 8. OCR Strategy

Many Vikaspedia PDFs are scanned rather than text-native.

Therefore the indexer uses a hybrid strategy:

``` text
PDF page
   |
   v
PyMuPDF text extraction
   |
   +---- >= usable text ----> use extracted text
   |
   +---- insufficient ------> render page image
                                  |
                                  v
                              Tesseract
                                  |
                                  v
                              OCR text
```

This is important because relying only on `pypdf`/PyMuPDF text
extraction would leave many scanned pages effectively empty.

The validated dataset contained approximately:

-   23 PDFs
-   80 original pages
-   77 documents/pages with usable text
-   approximately 101,265 extracted characters

These are validation-time values and can change when the source
collection is refreshed.

------------------------------------------------------------------------

# 9. Chunking

Whole PDFs are not sent to the LLM.

Documents are split into smaller text chunks.

Benefits:

-   Better retrieval precision
-   Smaller prompts
-   Lower token usage
-   Lower cost
-   Less irrelevant context

Each chunk retains metadata such as:

``` text
Source PDF
Page number
```

This metadata is later used for citations.

------------------------------------------------------------------------

# 10. Self-RAG

Self-RAG adds decision logic around normal RAG.

This project uses it for three major decisions:

### Decision 1 --- Scope

Is the question about agriculture/farmer support?

Example:

``` text
What is PM-KISAN?
```

Valid.

Example:

``` text
Who won yesterday's cricket match?
```

Out of scope.

### Decision 2 --- Evidence

Does the local PDF knowledge base contain sufficiently relevant
information?

If yes:

``` text
PDF evidence ---> LLM
```

If no:

``` text
Serper ---> LLM
```

### Decision 3 --- Freshness

Questions containing update/current language are routed toward live
search.

Examples include:

``` text
latest
recent
updates
announced
announcement
current
today
this month
this year
```

A specific current year combined with update language can also trigger
the live-search route.

------------------------------------------------------------------------

# 11. Low-Request Optimization

An early Self-RAG design could use an LLM for every step:

``` text
LLM scope classification
LLM document grading
LLM query rewrite
LLM generation
LLM answer grading
```

That creates unnecessary API requests.

This project deliberately moves practical decisions to deterministic
logic.

Normal flow is approximately:

``` text
Embedding request
      +
FAISS retrieval
      +
One main LLM generation request
```

Web fallback adds the search request:

``` text
Serper search
      +
One main LLM generation request
```

The application also limits:

-   Number of retrieved documents
-   PDF context length
-   Web result count
-   Web context length

This reduces cost, latency and rate-limit pressure.

------------------------------------------------------------------------

# 12. Web Search Fallback

The application uses Serper when local PDF evidence is insufficient or
the question clearly requires current information.

Example:

``` text
What farmer scheme updates were announced in India
in September 2026?
```

The local PDF collection cannot be assumed to contain every September
2026 announcement.

The routing becomes:

``` text
Question
   |
   v
Freshness detection
   |
   v
No static PDF answer
   |
   v
Serper
   |
   v
Search results
   |
   v
LLM
   |
   v
Answer + WEB sources
```

Validated result:

``` text
WEB: Demand for Grants...
WEB: 23rd Instalment of PM-KISAN...
WEB: Agriculture schemes...
```

This confirms Feature 12 is working.

------------------------------------------------------------------------

# 13. Source Citations

PDF sources are displayed with filename and page number.

Example:

``` text
PDF: Pradhan_Mantri_Kisan_Samman_Nidhi.pdf — page 1
```

Web sources are displayed with title and URL.

Example:

``` text
WEB: 23rd Instalment of PM-KISAN — https://...
```

The source metadata comes from retrieved evidence rather than being
invented as part of the answer.

------------------------------------------------------------------------

# 14. Error Handling

The application converts technical provider failures into safe customer
messages.

Examples of handled categories:

-   Rate limit
-   Quota
-   Authentication
-   Timeout
-   Retrieval error
-   Empty response
-   Generic LLM error

Customer example:

``` text
The AI service is temporarily unavailable because its
usage limit has been reached. Please try again later.
```

The application avoids exposing raw provider responses or credentials to
normal users.

Developer users can inspect controlled diagnostic details in Developer
Version.

------------------------------------------------------------------------

# 15. Developer Version --- Complete Explanation

The Developer Version is designed for **testing, debugging, tuning and
demonstrating the architecture**.

The customer interface should answer questions simply.

The developer interface must answer:

> What happened internally when this question was asked?

## 15.1 Developer Model Selector

Allows developers to select the configured generation model.

Validated model:

``` text
gpt-4.1-mini
```

Model choice affects:

-   Quality
-   Latency
-   Token usage
-   Cost

For a production deployment, model selection should normally be
controlled by configuration.

## 15.2 Temperature

Controls response variability.

Lower values are generally preferable for factual advisory applications.

``` text
Lower temperature
    |
    +--> More deterministic
    +--> Better for factual responses
```

Higher values can increase variation but are generally less desirable
for strict factual scheme information.

## 15.3 Retrieval `k`

Controls how many candidate documents/chunks are retrieved.

Example:

``` text
k = 4
```

Higher `k` may improve recall but can increase:

-   Irrelevant context
-   Prompt size
-   Token usage
-   Latency

The developer can tune this without changing the core code.

## 15.4 Web Max Results

Controls how many search results are considered.

More results can provide broader coverage but can also introduce
conflicting or low-quality information.

A small bounded result count keeps the prompt manageable.

## 15.5 Rebuild FAISS

Used after the source documents change.

Use it when:

-   New PDFs are downloaded
-   PDFs are replaced
-   OCR logic changes
-   Chunking changes
-   The index is missing

Command equivalent:

``` cmd
python -m rag.indexer
```

Do not rebuild the index for every chat question.

## 15.6 Diagnostics

The developer interface exposes operational status such as:

``` text
FAISS index: available
Serper web search: Enabled
```

The API key itself is never displayed.

If:

``` text
Serper web search: Not configured
```

the web fallback cannot operate.

## 15.7 Developer Chat

Developer Chat is used for controlled testing.

### PDF test

``` text
What is PM Kisan Samman Nidhi and what benefits does it provide?
```

Expected:

``` text
PDF sources
```

### Web fallback test

``` text
What farmer scheme updates were announced in India in September 2026?
```

Expected:

``` text
Web fallback used
WEB sources
```

### Out-of-scope test

``` text
who won yesterday cricket match
```

Expected:

``` text
Agriculture/farmer-support scope message
```

This confirms that unrelated questions are rejected before unnecessary
retrieval/search.

## 15.8 Developer Error Details

When an error occurs, Developer Version can show:

``` text
Error type
Technical exception
```

The customer still receives a safe friendly message.

## 15.9 LangSmith Monitoring

LangSmith provides a deeper view than the Streamlit diagnostics.

A validated trace showed:

``` text
LangGraph
   |
   +-- scope
   +-- retrieve
   +-- grade_documents
   +-- web_search
   +-- generate
   |     |
   |     +-- ChatOpenAI
   |
   +-- grade_answer
```

The validated trace also showed approximately:

``` text
Total execution: 6.33 seconds
Tokens: 1.411K
Cost: approximately $0.0007
Model: gpt-4.1-mini
```

The application tags traces with:

``` text
agri-farmer-adviser
rag-generation
```

and metadata identifying:

``` text
vikaspedia-agri-farmer-adviser
```

This is useful for production troubleshooting and cost/performance
analysis.

------------------------------------------------------------------------

# 16. Folder Structure

``` text
vikaspedia-agri-farmer-adviser/
|
+-- app_adviser.py
+-- requirements.txt
+-- .env
+-- .env.example
+-- README.md
+-- PRODUCTION_CHECKLIST.md
+-- PHASE3_UI.md
+-- pytest.ini
|
+-- config/
|   +-- production_defaults.json
|
+-- prompts/
|   +-- agri_farmer_adviser.md
|
+-- scraper/
|   +-- __init__.py
|   +-- vikaspedia.py
|   +-- downloader.py
|
+-- rag/
|   +-- __init__.py
|   +-- indexer.py
|   +-- index_manager.py
|   +-- llm.py
|   +-- prompts.py
|   +-- self_rag.py
|   +-- web_search.py
|
+-- tests/
|   +-- test_downloader.py
|   +-- test_indexer.py
|   +-- test_pagination.py
|   +-- test_pdf_download.py
|   +-- test_retrieval.py
|   +-- test_scope.py
|   +-- test_web_search_serper.py
|
+-- evals/
|   +-- evaluation_dataset.json
|   +-- evaluate.py
|
+-- data/
|   +-- faiss_index/
|       +-- index.faiss
|       +-- index.pkl
|
+-- downloads/
    +-- *.pdf
```

------------------------------------------------------------------------

# 17. File-by-File Responsibilities

## `app_adviser.py`

Main Streamlit entry point.

Responsibilities:

-   Customer UI
-   Developer Version
-   Chat handling
-   Streaming
-   Source display
-   Safe errors
-   Developer controls
-   Diagnostics

Run:

``` cmd
streamlit run app_adviser.py
```

## `scraper/vikaspedia.py`

Frozen production browser scraper.

Responsibilities:

-   Farmer Schemes listing
-   Pagination
-   Scheme discovery
-   Scheme navigation

Do not modify it simply to satisfy historical/debug tests.

## `scraper/downloader.py`

Handles PDF download operations.

Also treated as frozen production code.

## `rag/indexer.py`

Builds the searchable knowledge base.

Responsibilities:

-   PDF discovery
-   Text extraction
-   OCR fallback
-   Chunking
-   Embedding
-   FAISS index creation

Run:

``` cmd
python -m rag.indexer
```

## `rag/index_manager.py`

Loads/manages the persisted FAISS index.

## `rag/llm.py`

Creates/configures the LLM and LangSmith tracing configuration.

## `rag/prompts.py`

Stores RAG prompt definitions separately from application logic.

## `rag/self_rag.py`

Core orchestration component.

Responsibilities:

-   Scope routing
-   Retrieval
-   Relevance gate
-   Freshness routing
-   Web fallback
-   Context formatting
-   Generation
-   Answer grading
-   Error classification
-   LangGraph workflow

## `rag/web_search.py`

Web-search abstraction.

Current provider:

``` text
Serper
```

It normalizes results into:

``` text
title
url
content
```

Keeping the provider isolated makes future provider replacement easier.

## `config/production_defaults.json`

Stores application defaults/configuration values.

## `prompts/agri_farmer_adviser.md`

Domain-level adviser instructions.

## `evals/evaluation_dataset.json`

Contains predefined evaluation questions and expected behavior.

## `evals/evaluate.py`

Runs retrieval/full evaluation.

Retrieval-only:

``` cmd
python -m evals.evaluate --retrieval-only
```

Full:

``` cmd
python -m evals.evaluate
```

Full evaluation uses LLM requests, so avoid unnecessary repeated runs
when API limits are tight.

## `tests/`

Unit/integration tests created during development.

Some historical tests may reflect earlier interfaces and therefore are
not the sole production acceptance criterion.

The acceptance decision should prioritize:

-   End-to-end application behavior
-   Evaluation results
-   Source validation
-   Web fallback validation
-   Error handling
-   LangSmith tracing

## `data/faiss_index/`

Persisted FAISS files:

``` text
index.faiss
index.pkl
```

## `downloads/`

Downloaded source PDFs.

------------------------------------------------------------------------

# 18. Environment Configuration

Create `.env`:

``` env
OPENAI_API_KEY=your-openai-key

SERPER_API_KEY=your-serper-key

LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your-langsmith-key
LANGSMITH_PROJECT=vikaspedia-agri-farmer-adviser
```

Never commit real keys.

`.env` should be in `.gitignore`.

Use `.env.example` to document required variables without secrets.

------------------------------------------------------------------------

# 19. Installation

Create virtual environment:

``` cmd
python -m venv venv
```

Activate:

``` cmd
venv\Scripts\activate
```

Install Python dependencies:

``` cmd
pip install -r requirements.txt
```

Install Tesseract:

``` cmd
winget install UB-Mannheim.TesseractOCR
```

Verify:

``` cmd
"C:\Program Files\Tesseract-OCR\tesseract.exe" --version
```

------------------------------------------------------------------------

# 20. Build FAISS

After PDFs are present in `downloads/`:

``` cmd
python -m rag.indexer
```

The generated index is stored under:

``` text
data/faiss_index/
```

------------------------------------------------------------------------

# 21. Start the Application

``` cmd
streamlit run app_adviser.py
```

Stop:

``` text
Ctrl+C
```

------------------------------------------------------------------------

# 22. Testing

## Test A --- PDF RAG

Question:

``` text
What is PM Kisan Samman Nidhi and what benefits does it provide?
```

Expected:

-   Grounded answer
-   PDF source citations

## Test B --- Web fallback

Question:

``` text
What farmer scheme updates were announced in India in September 2026?
```

Expected:

-   Current-information routing
-   Serper search
-   `WEB:` sources

## Test C --- Out of scope

Question:

``` text
who won yesterday cricket match
```

Expected:

-   Friendly agriculture-scope response
-   No unnecessary web search

## Test D --- Retrieval evaluation

``` cmd
python -m evals.evaluate --retrieval-only
```

Validated:

``` text
Passed: 10/10
Pass rate: 100.0%
```

## Test E --- LangSmith

Generate a question and verify a trace contains nodes such as:

``` text
scope
retrieve
grade_documents
generate
ChatOpenAI
grade_answer
```

For a web-fallback question:

``` text
web_search
```

should also appear.

------------------------------------------------------------------------

# 23. Why Some Technologies Were Chosen

  --------------------------------------------------------------------------
  Requirement             Selected technology        Reason
  ----------------------- -------------------------- -----------------------
  Browser automation      Playwright                 Reliable modern browser
                                                     automation

  PDF extraction          PyMuPDF                    Fast local PDF
                                                     processing

  Scanned PDF extraction  Tesseract                  OCR fallback

  Vector search           FAISS                      Local, fast and simple

  Embeddings              OpenAI                     Compact semantic
                          `text-embedding-3-small`   embedding

  LLM                     `gpt-4.1-mini`             Good balance of
                                                     quality/cost

  RAG orchestration       LangChain                  AI integration

  Workflow                LangGraph                  Explicit Self-RAG graph

  UI                      Streamlit                  Python-only rapid
                                                     application UI

  Web fallback            Serper                     Live search with
                                                     practical free
                                                     development option

  Monitoring              LangSmith                  Tracing and
                                                     observability
  --------------------------------------------------------------------------

------------------------------------------------------------------------

# 24. Security

Never place credentials in source code.

Bad:

``` python
OPENAI_API_KEY = "real-key"
```

Good:

``` env
OPENAI_API_KEY=real-key
```

Do not commit:

``` text
.env
```

Do not expose API keys in screenshots, GitHub, logs or chat.

------------------------------------------------------------------------

# 25. Cost and Performance Principles

The architecture follows several optimization principles:

1.  Reject irrelevant questions early.
2.  Avoid unnecessary LLM classification calls.
3.  Limit FAISS retrieval count.
4.  Limit PDF context.
5.  Limit web results.
6.  Limit web context.
7.  Use one primary generation call.
8.  Use LangSmith to observe latency/token/cost behavior.

This makes the application easier to operate under API request limits.

------------------------------------------------------------------------

# 26. Future Enhancements

The following are deliberately outside the current frozen scope.

## State-aware answers

Allow:

``` text
Tamil Nadu
Karnataka
Kerala
Maharashtra
...
```

and prioritize state-specific schemes.

## Farmer profile

Potential inputs:

``` text
State
Crop
Land size
Farmer category
Irrigation type
```

Then recommend suitable schemes.

## Better web-source ranking

Prefer:

``` text
PIB
Central government ministries
State government websites
Vikaspedia
Other trusted sources
```

over blogs/social/commercial sources when possible.

## Scheduled refresh

Automate:

``` text
Scrape
  |
Download
  |
OCR
  |
Re-index
```

## Advanced evaluation

Measure:

-   Answer correctness
-   Faithfulness
-   Citation correctness
-   Source quality
-   Latency
-   Token usage
-   Cost

## Authentication

Add login and role-based access for production deployment.

## Voice

Potential architecture:

``` text
Speech
  |
  v
Speech-to-text
  |
  v
RAG
  |
  v
Text-to-speech
```

## Persistent conversation memory

Could be added in a future release, but it is not part of the current
frozen scope.

------------------------------------------------------------------------

# 27. Troubleshooting

## Streamlit does not start

Activate the environment:

``` cmd
venv\Scripts\activate
```

Then:

``` cmd
streamlit run app_adviser.py
```

## FAISS index unavailable

Run:

``` cmd
python -m rag.indexer
```

## OCR unavailable

Verify:

``` cmd
"C:\Program Files\Tesseract-OCR\tesseract.exe" --version
```

## Serper not configured

Verify `.env` contains:

``` env
SERPER_API_KEY=your-serper-key
```

Restart:

``` cmd
Ctrl+C
streamlit run app_adviser.py
```

Developer Version should display:

``` text
Serper web search: Enabled
```

## LangSmith not showing traces

Verify:

``` env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your-langsmith-key
LANGSMITH_PROJECT=vikaspedia-agri-farmer-adviser
```

Restart the application and generate a new request.

## OpenAI 429

A 429 can result from request-rate limits, daily limits, quota or
billing/spend limits.

Avoid repeated retries when the underlying issue is quota/billing.

The low-request design exists partly to reduce this problem.

------------------------------------------------------------------------

# 28. Developer Learning Guide

A beginner can understand the project in this order:

### Step 1

Learn:

``` text
Python
```

### Step 2

Understand:

``` text
PDF
OCR
```

### Step 3

Understand:

``` text
Embedding
Vector
FAISS
```

### Step 4

Understand:

``` text
RAG
```

### Step 5

Understand:

``` text
LangChain
```

### Step 6

Understand:

``` text
LangGraph
Self-RAG
```

### Step 7

Understand:

``` text
Web Search Fallback
```

### Step 8

Understand:

``` text
LangSmith
```

A useful mental model is:

``` text
Playwright = gets the knowledge
Tesseract = reads scanned knowledge
FAISS = finds relevant knowledge
RAG = gives knowledge to the LLM
Self-RAG = decides which knowledge path to use
Serper = supplies live information
LLM = writes the final answer
Streamlit = displays the application
LangSmith = watches what happened
```

------------------------------------------------------------------------

# 29. Final Architecture in One Diagram

``` text
                     VIKASPEDIA
                         |
                         v
                 Playwright Scraper
                         |
                         v
                    PDF Files
                         |
                         v
              PyMuPDF + Tesseract
                         |
                         v
                    Text Chunks
                         |
                         v
               OpenAI Embeddings
                         |
                         v
                      FAISS
                         |
                         |
                         v
User ---> Streamlit ---> Self-RAG
                           |
                +----------+----------+
                |                     |
          Out of Scope           In Scope
                |                     |
                v                     v
            Response              Decision
                                      |
                            +---------+---------+
                            |                   |
                       Strong PDF         Current/weak
                            |                   |
                            v                   v
                           PDF               Serper
                         context           web search
                            |                   |
                            +---------+---------+
                                      |
                                      v
                                  OpenAI LLM
                                      |
                                      v
                                Final Answer
                                      |
                              +-------+-------+
                              |               |
                         PDF Sources      WEB Sources
                                      |
                                      v
                                  LangSmith
```

------------------------------------------------------------------------

# 30. Final Takeaway

This project demonstrates a complete practical GenAI application rather
than a simple chatbot.

The most important architectural lessons are:

``` text
LLM alone
   !=
Reliable domain application
```

Instead:

``` text
Domain documents
      +
OCR
      +
Embeddings
      +
Vector retrieval
      +
RAG
      +
Self-RAG routing
      +
Live web fallback
      +
Source citations
      +
Error handling
      +
Evaluation
      +
Observability
      =
Production-oriented GenAI application
```

The project therefore demonstrates the full journey from **source-data
acquisition to retrieval, reasoning/routing, grounded generation,
evaluation and monitoring**.
