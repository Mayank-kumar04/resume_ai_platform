# 🎯 ResumeAI Platform

> A modern AI-powered desktop application for ATS resume optimization — built with Python, PyQt5, and NLP.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green?style=flat-square)
![SQLite](https://img.shields.io/badge/DB-SQLite-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-purple?style=flat-square)

---

## ✨ Features

| Feature                       | Description                                                                                                     |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------- |
| **ATS Scoring Engine**        | Weighted 6-category score (keyword 30%, formatting 20%, grammar 15%, structure 15%, impact 10%, compliance 10%) |
| **Job Description Analyzer**  | Extracts required/preferred skills, seniority, tools, and experience level from pasted JD text                  |
| **Resume ↔ JD Matcher**       | TF-IDF cosine similarity + keyword overlap to calculate match %                                                 |
| **Grammar & Writing Checker** | LanguageTool integration + regex fallback for passive voice, weak phrases                                       |
| **Action Verb Enhancer**      | Detects weak verbs ("worked on", "responsible for") and suggests contextual replacements                        |
| **Impact Quantifier**         | Flags un-quantified bullet points and suggests how to add measurable outcomes                                   |
| **Link Validator**            | Concurrent HTTP validation of GitHub, LinkedIn, portfolio, and certificate URLs                                 |
| **Section Quality Analyzer**  | Evaluates Summary, Experience, Skills, Projects, Education individually                                         |
| **Skill Gap Engine**          | Prioritized missing skills based on JD requirements + industry frequency data                                   |
| **Template Compliance**       | Detects multi-column layouts, excessive whitespace, missing headings                                            |
| **Benchmark Comparison**      | Radar chart comparison of your resume vs a high-performing benchmark                                            |
| **Report Exporter**           | HTML and plain-text reports with full score breakdown                                                           |
| **SQLite Persistence**        | All sessions, reports, and JDs stored locally                                                                   |
| **Dark Theme UI**             | Modern SaaS-style dark theme with PyQt5                                                                         |

---

## 🖼️ Screenshots

| Dashboard                     | Analysis                      | Suggestions                     |
| ----------------------------- | ----------------------------- | ------------------------------- |
| (./screenshots/dashboard.png) | (./screenshots/analysis.png`) | (./screenshots/suggestions.png) |

| Benchmark                     | Analysis2                     | Reports and History                 |
| ----------------------------- | ----------------------------- | ----------------------------------- |
| (./screenshots/benchmark.png) | (./screenshots/analysis2.png) | (./screenshots/reports_history.png) |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Java (for LanguageTool grammar engine) — optional, app falls back gracefully

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/resume-ai-platform.git
cd resume-ai-platform

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download spaCy model (optional, for future NLP features)
python -m spacy download en_core_web_sm

# 5. Run the app
python main.py
```

### Usage

1. **Upload Resume** → drag & drop or browse for your resume PDF
2. **Add Job Description** → paste the full JD text and click Save
3. **Click "▶ Run Analysis"** in the top bar
4. View results across:
   - **Dashboard** — ATS score overview
   - **Analysis** — detailed category breakdown, keyword match, grammar, link validation
   - **Suggestions** — action verb fixes, quantification tips, skill gap
   - **Benchmark** — upload a benchmark PDF to compare
   - **Reports** — export HTML or TXT report

---

## 🏗️ Architecture

```
resume_ai_platform/
│
├── main.py                    # Entry point
├── database.py                # SQLite ORM (DatabaseManager singleton)
├── requirements.txt
│
├── ui/                        # PyQt5 UI layer
│   ├── main_window.py         # Root window, sidebar, topbar, page routing
│   ├── dashboard.py           # Score overview + category cards
│   ├── upload_page.py         # Drag-and-drop PDF upload
│   ├── jd_page.py             # JD paste + live keyword preview
│   ├── analysis_page.py       # Full ATS results display
│   ├── benchmark_page.py      # Radar chart + dimension comparison
│   ├── suggestions_page.py    # Verb fixes + impact + skill gap
│   ├── reports_page.py        # Export HTML/TXT + history table
│   ├── settings_page.py       # App preferences
│   ├── progress_dialog.py     # Analysis progress modal
│   ├── components.py          # ScoreCard, MetricCard, Badge, EmptyState, …
│   ├── base_page.py           # BasePage (scrollable, on_activate hook)
│   └── styles.py              # Global QSS dark theme + COLORS dict
│
├── parser/
│   └── resume_parser.py       # pdfplumber PDF → ResumeData
│
├── analysis/
│   ├── ats_engine.py          # Weighted ATS scoring (ATSScorer)
│   ├── jd_analyzer.py         # JD keyword/skill/seniority extraction
│   ├── resume_matcher.py      # TF-IDF cosine similarity + keyword overlap
│   ├── grammar_checker.py     # LanguageTool + regex fallback
│   ├── action_verbs.py        # Weak verb detection + contextual suggestions
│   ├── impact_engine.py       # Unquantified bullet detection
│   ├── link_validator.py      # Concurrent HTTP URL validation
│   ├── section_analyzer.py    # Per-section quality scoring
│   ├── skill_gap.py           # Prioritized skill gap + learning path
│   ├── template_checker.py    # ATS layout compliance heuristics
│   └── benchmark_engine.py    # Resume vs benchmark comparison
│
├── charts/
│   └── chart_builder.py       # matplotlib charts embedded in PyQt5
│
├── utils/
│   ├── analysis_worker.py     # QThread orchestrating all engines
│   └── report_exporter.py     # HTML + TXT report generation
│
├── exports/                   # Default HTML/TXT export output
└── reports/                   # Report files
```

---

## 🧠 ATS Scoring Methodology

| Category         | Weight | How It's Measured                                                   |
| ---------------- | ------ | ------------------------------------------------------------------- |
| Keyword Match    | 30%    | % of JD keywords found in resume (whole-word regex + TF-IDF cosine) |
| Formatting       | 20%    | Page count, word count, bullet density, contact info completeness   |
| Grammar          | 15%    | LanguageTool issue count (proportional deduction)                   |
| Resume Structure | 15%    | Presence of Summary, Experience, Education, Skills, Projects        |
| Impact Writing   | 10%    | Quantified bullets %, strong action verb density                    |
| ATS Compliance   | 10%    | Multi-column detection, heading clarity, long-line heuristics       |

All scores are deterministic and explainable — **no random values**.

---

## 🔧 Tech Stack

| Layer       | Technology                               |
| ----------- | ---------------------------------------- |
| Language    | Python 3.10+                             |
| GUI         | PyQt5                                    |
| PDF Parsing | pdfplumber                               |
| NLP         | spaCy, scikit-learn                      |
| Grammar     | language-tool-python                     |
| Charts      | matplotlib (FigureCanvas embedded in Qt) |
| Database    | SQLite (via Python's sqlite3)            |
| HTTP        | requests (concurrent link validation)    |
| Packaging   | PyInstaller                              |

---

## 📦 Build Executable

```bash
pyinstaller --onefile --windowed --name ResumeAI main.py
```

---

## 🔮 Future Improvements

- [ ] spaCy NER for smarter entity and skill extraction
- [ ] OpenAI / Claude API integration for AI-generated rewrite suggestions
- [ ] Real-time JD scraping from LinkedIn / Indeed (with consent)
- [ ] Multi-resume comparison mode
- [ ] Light theme toggle
- [ ] Resume template generator
- [ ] Cloud sync via SQLite + S3

---

## 📄 License

MIT — free to use, modify, and distribute.

---

> Built as a portfolio project demonstrating: GUI engineering, NLP pipelines, modular OOP architecture, and real-world ATS heuristics.
