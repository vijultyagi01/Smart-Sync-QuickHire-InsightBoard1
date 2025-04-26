⚙️ Smart-Sync-QuickHire + Skill Gap Course Recommender Suite
🔍 AI-Powered Resume–JD Matcher and Dynamic Skill Gap Filler
“Sync Talent. Fill Gaps. Hire Smarter. Faster. Better.”

🚀 Project Overview
The Smart-Sync-QuickHire + Skill Gap Course Recommender Suite is a complete AI-powered hiring platform that:

Matches multiple candidate CVs against job descriptions (JDs)

Identifies skill gaps intelligently

Recommends personalized online courses to fill missing skills

Generates individual PDF reports for candidates

Provides an interactive dashboard for recruiter insights

All built using sleek, powerful Streamlit web apps.

💡 Key Features
✅ Multi-CV to JD Skill Matching
✅ TF-IDF and NLP-Based Skill Extraction
✅ Skill Gap Detection and Reporting
✅ Personalized Course Recommendations
✅ Candidate-Specific PDF Report Generation (with clickable links)
✅ Bulk Download of All Reports as ZIP
✅ Interactive Dashboards for Recruiters
✅ Interview Slot Booking System
✅ Email Notification System (Mocked)
✅ 100% Local Processing — No Paid APIs

📊 Dashboard Insights

Section	Description
📌 Summary Metrics	Total CVs processed, Matched Skills, Final Rankings
📉 Top Missing Skills	Most common missing skills across candidates
📈 Candidate Performance	Matched skill counts per candidate (visualized)
❌ Skill Gap Analysis	Frequently missing skills across all CVs
🧠 Smart Skill Search	Filter candidates by selected skills
📦 Download Hub	Individual or bulk download of candidate PDF reports
🛠️ Tech Stack
Language: Python 3.8+

Frontend Framework: Streamlit

Natural Language Processing: spaCy, TF-IDF

Visualization: Plotly, pandas

File Parsing: pdfplumber

PDF Generation: FPDF

Concurrency: ThreadPoolExecutor (for faster CV processing)

Encoding: Base64 (for secure file downloads)

▶️ Running the Applications
1.Smart-Sync-QuickHire (Resume Matcher + Dashboard)

bash
Copy
Edit
cd "C:\Users\Admin\Downloads\autorag (7)\autorag"
 streamlit run myapps.py

2.Candidate Course Recommender (Skill Gap → Course Recommendations)

bash
Copy
Edit
cd C:\Users\Admin\Downloads\
streamlit run myapps2.py

