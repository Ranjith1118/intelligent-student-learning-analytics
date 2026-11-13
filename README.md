# Intelligent Student Learning Analytics Platform

## Features
- Overview dashboard with score, attendance, submission metrics and charts
- Class and subject filters
- Student-level summaries
- Transparent, rule-based support signals
- Suggested supportive actions and downloadable intervention plan
- Prompt template comparison
- Offline learning-support chatbot
- Synthetic demo dataset with 27 subjects, including Python, Java, SQL, C/C++, HTML/CSS, JavaScript, DBMS, Data Structures, AI, Machine Learning, Cloud Computing, Cybersecurity and more

## Requirements
Python 3.10+ (Python 3.11 recommended)

## Setup in Windows / VS Code
Open this folder in VS Code. In the terminal, run these commands one at a time:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app.py
```

If PowerShell blocks activation, use Command Prompt and run:
```bat
venv\Scripts\activate.bat
```

Then open the local URL shown in the terminal (usually http://localhost:8501).

## Environment file
A `.env` file is included as a template. The current application does not require an API key because the chatbot is rule-based. If you later connect an LLM, add your key locally and never commit it.

## Data
The CSV contains synthetic demonstration records only. It is not real student data and must not be treated as a validated predictive dataset.

## Limitations and privacy
- Support priority is a transparent heuristic, not a trained or validated predictive model.
- Do not use output alone for grades, admissions, discipline, or other consequential decisions.
- Protect student data and obtain appropriate authorization before using real records.
