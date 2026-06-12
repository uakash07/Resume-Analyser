# 📄 AI Resume Analyzer

## 1. Project Overview

The AI Resume Analyzer is a Streamlit-based web application that uses Google Gemini Flash AI to analyze resumes against job descriptions and produce structured ATS-style feedback. It supports both single-resume analysis and bulk multi-resume ranking, making it useful for both job seekers and recruiters. The system extracts text from PDF resumes, sends them to Gemini with a structured prompt, and presents match percentages, skill gaps, strengths, and personalized improvement suggestions.

---

## 2. Tech Stack

| Component       | Library              | Version   | Why This Was Chosen                                                  |
|-----------------|----------------------|-----------|----------------------------------------------------------------------|
| Frontend/UI     | Streamlit            | 1.45.1    | Rapid Python-native UI with no HTML/CSS required; perfect for AI apps |
| PDF Extraction  | PyMuPDF (fitz)       | 1.26.1    | Fastest and most accurate PDF text extractor; handles complex layouts |
| AI Analysis     | google-generativeai  | 0.8.5     | Free Gemini Flash API; fast, capable, structured JSON output          |
| Data Handling   | pandas               | 2.2.3     | Industry-standard DataFrame library; ideal for sorting/ranking tables |
| Env Management  | python-dotenv        | 1.0.1     | Safely loads secrets from .env without hardcoding API keys in code    |

---

## 3. Folder Structure

```
Resume_analyzer/
│
├── app.py                  # Main Streamlit app; handles UI and orchestrates all modules
├── modules/
│   ├── __init__.py         # Exposes all module functions as a clean package API
│   ├── pdf_reader.py       # Extracts raw text from uploaded PDF files using PyMuPDF
│   ├── analyzer.py         # Sends resume + JD to Gemini Flash and returns parsed JSON dict
│   └── ranker.py           # Takes list of result dicts, returns sorted pandas DataFrame
│
├── .env                    # Stores GEMINI_API_KEY secret (never committed to Git)
├── .gitignore              # Prevents .env, __pycache__, and .pyc files from being tracked
├── requirements.txt        # All Python dependencies with pinned versions
└── README.md               # Full project documentation (this file)
```

---

## 4. How Files Are Connected (THE MOST IMPORTANT SECTION)

This section traces the exact data flow through the system for both modes.

---

### 🔁 Single Resume Flow

**Step 1: User uploads PDF in `app.py`**
The Streamlit `st.file_uploader` widget in `app.py` receives the PDF file as a file-like object. This connects `app.py` to `pdf_reader.py` because `app.py` passes this object directly to `extract_text()`.

**Step 2: `app.py` calls `extract_text()` from `pdf_reader.py`**
The uploaded file object is passed as the argument to `extract_text()`. This connects `app.py` to `pdf_reader.py` because `app.py` imports and delegates the reading responsibility to the reader module.

**Step 3: `pdf_reader.py` uses PyMuPDF to extract raw text and returns a string**
Inside `extract_text()`, PyMuPDF opens the file from bytes, iterates every page, and concatenates all page text into a single clean string. This connects `pdf_reader.py` back to `app.py` because the returned string is the primary input for the next stage.

**Step 4: `app.py` passes that string + job description to `analyze_resume()` in `analyzer.py`**
The extracted text (from Step 3) and the job description (typed by the user in `st.text_area`) are both passed to `analyze_resume()`. This connects `app.py` to `analyzer.py` because `app.py` has the UI inputs but delegates all AI logic to `analyzer.py`.

**Step 5: `analyzer.py` sends both to Gemini Flash API with a structured prompt**
Inside `analyze_resume()`, the resume text and job description are injected into a carefully crafted prompt that instructs Gemini to respond in strict JSON format only. This connects `analyzer.py` to the external Gemini API because the function makes an HTTP call via the `google-generativeai` SDK.

**Step 6: Gemini returns JSON, `analyzer.py` parses it and returns a Python dict**
The raw response text from Gemini is cleaned (markdown code fences removed), then parsed with `json.loads()`. The resulting Python dict is returned to the caller. This connects `analyzer.py` back to `app.py` because the dict is the structured data `app.py` needs to render the UI.

**Step 7: `app.py` reads the dict and renders each field in Streamlit UI**
`app.py` reads keys like `match_percentage`, `matching_skills`, `missing_skills`, `strengths`, `improvements`, `ai_suggestions`, and `recommendation` from the dict and renders them using Streamlit widgets. This is the final output stage for single mode.

---

### 🔁 Bulk Resume Flow (Steps 8–10 are added on top of Steps 1–7)

**Step 8 (Bulk only): `app.py` collects all dicts into a list and passes to `rank_candidates()` in `ranker.py`**
For each uploaded PDF, Steps 1–6 repeat. After all resumes are processed, `app.py` collects all result dicts into a list and passes it to `rank_candidates()`. This connects `app.py` to `ranker.py` because `app.py` has the full list of analyzed results but delegates sorting and formatting to `ranker.py`.

**Step 9 (Bulk only): `ranker.py` uses pandas to sort and return a DataFrame**
Inside `rank_candidates()`, pandas creates a DataFrame, sorts by `match_percentage` descending, resets the index to start from 1 (representing rank), and renames columns for display. This connects `ranker.py` back to `app.py` because the sorted DataFrame is returned for table rendering.

**Step 10 (Bulk only): `app.py` displays the ranked DataFrame as a styled table**
`app.py` applies a `highlight_top3` style function to the DataFrame and renders it with `st.dataframe`. Top 3 candidates get a green background highlight. This is the final output stage for bulk mode.

---

## 5. Setup Instructions

**Step 1: Clone or download the project**
```
git clone <repo-url>
cd Resume_analyzer
```

**Step 2: Create a virtual environment**
```
python -m venv venv
```

**Step 3: Activate the virtual environment**
- Windows: `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

**Step 4: Install all dependencies**
```
pip install -r requirements.txt
```

**Step 5: Get your free Gemini API key**
Visit [https://aistudio.google.com](https://aistudio.google.com), sign in with Google, and create a free API key.

**Step 6: Create the `.env` file**
```
GEMINI_API_KEY=your_actual_key_here
```

**Step 7: Run the application**
```
streamlit run app.py
```
The app will open at `http://localhost:8501` in your browser.

---

## 6. How To Use

### Single Resume Analysis
1. Select **"Single Resume Analysis"** from the radio buttons at the top.
2. Click **"Upload Resume (PDF)"** and select one PDF resume.
3. Paste the job description into the text area on the right.
4. Click **"🚀 Analyze Resume"**.
5. View the ATS Match Score, skill badges, strengths, improvements, and AI suggestions.

### Bulk Resume Ranking
1. Select **"Bulk Resume Ranking"** from the radio buttons at the top.
2. Click **"Upload Multiple Resumes (PDF)"** and select multiple PDFs at once.
3. Paste the same job description into the text area.
4. Click **"🚀 Analyze All Resumes"**.
5. Watch the progress bar as each resume is analyzed.
6. View the ranked table (top 3 highlighted green) and expand each candidate for detailed results.

---

## 7. Project Review Q&A

**Q1: Why did you choose Streamlit over Flask or Django?**
A: Streamlit lets you build interactive data apps entirely in Python with zero HTML, CSS, or JavaScript. Flask and Django require template files, routing logic, and front-end code. For an AI tool focused on data presentation, Streamlit is 10x faster to build and maintain.

**Q2: Why PyMuPDF over PyPDF2?**
A: PyMuPDF (fitz) is significantly faster, more accurate, and handles complex PDF layouts, multi-column text, and embedded fonts far better than PyPDF2. PyPDF2 is an older library that frequently fails on modern PDFs and has poor Unicode support.

**Q3: Why Gemini Flash over GPT-4?**
A: Gemini Flash is free to use via the Google AI Studio API with generous rate limits, whereas GPT-4 requires a paid OpenAI account. For this project's use case (structured JSON extraction), Gemini Flash performs comparably to GPT-4 at zero cost.

**Q4: Why use pandas for ranking instead of just sorting a list?**
A: Pandas provides a DataFrame structure that integrates directly with Streamlit's `st.dataframe` and supports built-in styling (e.g., `df.style.apply`). Sorting a plain list would require manual column handling and couldn't produce the styled table output.

**Q5: Why use a `.env` file for the API key instead of hardcoding it?**
A: Hardcoding secrets in source code is a serious security risk — anyone with access to the repo can steal the key. The `.env` file is listed in `.gitignore` so it's never committed, and `python-dotenv` loads it at runtime safely.

**Q6: What is TF-IDF and why did you NOT use it?**
A: TF-IDF (Term Frequency–Inverse Document Frequency) is a statistical method that scores how important a word is in a document relative to a corpus. It could be used to compute keyword overlap between a resume and job description. We did NOT use it because Gemini AI performs semantic understanding — it recognizes that "JS" and "JavaScript" are the same skill, whereas TF-IDF only does exact string matching. AI-based analysis is far more accurate.

**Q7: What happens if the Gemini API is down?**
A: The `try/except` block in `analyzer.py` catches all exceptions from the API call. If the API is unavailable, it returns a dict with an `"error"` key. `app.py` checks for this key and displays a user-friendly `st.error()` message instead of crashing.

**Q8: How does the JSON parsing work?**
A: Gemini is prompted to return only valid JSON with no markdown. But as a safeguard, the code strips any ` ```json ` or ` ``` ` code fences using string operations before calling `json.loads()`. If parsing still fails (e.g., malformed response), a `json.JSONDecodeError` is caught and an error dict is returned.

**Q9: What is the match percentage based on?**
A: The match percentage is determined entirely by Gemini's semantic analysis of the resume vs. the job description. Gemini evaluates skill overlap, experience alignment, keyword density, and role fit — not just keyword counting. It returns an integer between 0 and 100.

**Q10: How does bulk mode handle 30+ resumes?**
A: Each resume is processed sequentially in a for loop. A progress bar tracks completion. If any individual resume fails (bad PDF, API error), it is skipped with a warning and the loop continues. All successful results are collected and ranked at the end. For 30+ resumes, this may take a few minutes on the free Gemini tier due to rate limits.

**Q11: What are the limitations of this system?**
A: (1) Cannot extract text from scanned/image-based PDFs — OCR is not implemented. (2) Free Gemini API has rate limits (~15 requests/minute), causing slowdowns for large batches. (3) Results are only as good as Gemini's interpretation — no ground truth validation. (4) No persistent storage; results are lost on page refresh.

**Q12: How would you scale this to 1000 resumes?**
A: Use async API calls with `asyncio` to process multiple resumes in parallel. Implement a queue system (e.g., Celery + Redis) to manage API rate limits. Store results in a database (PostgreSQL/SQLite) to persist between sessions. Add batch processing with retry logic for failed API calls.

**Q13: What is ATS and how does this project simulate it?**
A: ATS stands for Applicant Tracking System — software recruiters use to automatically screen resumes by parsing keywords and comparing them to job requirements. This project simulates ATS by extracting resume text, comparing it to a JD using AI, and scoring the match — mimicking what real ATS platforms like Workday or Greenhouse do algorithmically.

**Q14: Why python-dotenv and not `os.environ` directly?**
A: `os.environ` reads system-level environment variables that must be manually set for each session. `python-dotenv` automatically reads from a `.env` file at project load time, making setup portable and consistent across different machines and developers without manual configuration.

**Q15: How would you add a database to this project?**
A: Add SQLite (via `sqlite3`) or PostgreSQL (via `psycopg2`) to store each analysis result. Create a table with columns: `id`, `candidate_name`, `job_title`, `match_percentage`, `recommendation`, `timestamp`. On each analysis, insert the result. Add a new Streamlit page to view historical analyses and compare across multiple job postings.

**Q16: What is the role of `__init__.py`?**
A: `__init__.py` marks the `modules/` directory as a Python package. Without it, Python cannot import from `modules`. It also re-exports the three functions (`extract_text`, `analyze_resume`, `rank_candidates`) so `app.py` can use `from modules import ...` instead of importing from each submodule separately.

**Q17: Why put code in a `modules/` folder instead of one big file?**
A: Separation of concerns — each module has one job. `pdf_reader.py` only reads PDFs. `analyzer.py` only talks to the AI. `ranker.py` only sorts data. This makes the code easier to test, debug, and maintain. If the AI provider changes from Gemini to OpenAI, only `analyzer.py` needs editing.

**Q18: How does Gemini Flash differ from Gemini Pro?**
A: Gemini Flash is optimized for speed and efficiency — it responds faster and costs less (or is free) but is slightly less capable on complex reasoning tasks. Gemini Pro is more powerful for nuanced analysis but slower and has stricter rate limits. For structured JSON extraction tasks like resume analysis, Flash performs equally well in practice.

**Q19: What future features can be added?**
A: (1) Resume rewriter — auto-improve resume text to better match the JD. (2) Resume chatbot — let users ask follow-up questions about their results. (3) ATS score breakdown with visual charts (radar chart per skill category). (4) Recruiter dashboard with filters, sort, and export to Excel. (5) Cover letter generator. (6) OCR support for scanned PDFs using Tesseract.

**Q20: What is the time complexity of the ranking algorithm?**
A: The ranking uses `pandas.DataFrame.sort_values()` which internally uses a hybrid sort (Timsort). Time complexity is **O(n log n)** where n is the number of candidates. For practical purposes (even 1000 resumes), this is near-instantaneous — the bottleneck is always the Gemini API calls, not the ranking.

---

## 8. Known Limitations

- **API Rate Limits:** The free Gemini API tier allows approximately 15 requests per minute. Processing more than 15 resumes rapidly will trigger rate limit errors.
- **Scanned PDFs:** PyMuPDF can only extract text from text-based PDFs. Scanned or image-only PDFs will return empty text. OCR (e.g., Tesseract) would be needed to handle these.
- **AI Response Quality:** Results depend on Gemini's interpretation of the resume and job description. Unusual formatting or very short resumes may produce less accurate analysis.
- **No Persistence:** All results are lost when the Streamlit session ends or the page is refreshed. A database would be needed for persistence.

---

## 9. Future Enhancements

- **Resume Chatbot:** After analysis, allow users to chat with an AI about their results ("What should I improve first?").
- **ATS Score Breakdown:** Show a radar/spider chart breaking down the score by categories: Technical Skills, Experience, Education, Keywords.
- **Resume Rewriter:** Automatically rewrite resume bullet points to better match the job description's language and keywords.
- **Recruiter Dashboard:** Full dashboard with charts, filters, CSV export, and candidate comparison across multiple job openings.
- **OCR Support:** Integrate Tesseract OCR to handle scanned/image-based PDF resumes.
- **Cover Letter Generator:** Generate a tailored cover letter based on the resume and job description.
