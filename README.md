⚙️ Smart-Sync-QuickHire + Skill Gap Course Recommender Suite
🔍 AI-Powered Resume–JD Matcher and Dynamic Skill Gap Filler

“Sync Talent. Fill Gaps. Hire Smarter. Faster. Better.”

🚀 Project Overview
The Smart-Sync-QuickHire + Skill Gap Course Recommender Suite is a complete AI-powered hiring platform that:

📄 Matches multiple candidate CVs against Job Descriptions (JDs)

🧩 Identifies candidate skill gaps intelligently

🎯 Recommends personalized online courses to bridge missing skills

📑 Generates professional, candidate-specific PDF reports

📊 Provides recruiters with interactive dashboards for insights

Built with sleek, powerful Streamlit web apps, 100% local — no cloud dependencies!

💡 Key Features
✅ Multi-CV to JD Skill Matching
✅ TF-IDF and NLP-Based Skill Extraction
✅ Skill Gap Detection and Reporting
✅ Personalized Course Recommendations
✅ Candidate-Specific PDF Report Generation (with Clickable Links)
✅ Bulk Download of All Reports as ZIP
✅ Interactive Dashboards for Recruiters
✅ Interview Slot Booking System
✅ Email Notification System (Mocked)
✅ Fully Local Processing — No Paid APIs Required

📊 Dashboard Insights

Section	Description
📌 Summary Metrics	Total CVs processed, Matched Skills, Final Rankings
📉 Top Missing Skills	Most common missing skills across candidates
📈 Candidate Performance	Matched skill counts per candidate (visualized)
❌ Skill Gap Analysis	Frequently missing skills across all CVs
🧠 Smart Skill Search	Filter candidates by selected skills
📦 Download Hub	Download individual or all candidate PDF reports
🛠️ Tech Stack
Language: Python 3.8+

Frontend Framework: Streamlit

Natural Language Processing: spaCy, TF-IDF

Visualization: Plotly, pandas

File Parsing: pdfplumber

PDF Report Generation: FPDF

Concurrency for Fast Processing: ThreadPoolExecutor

Secure File Downloads: Base64 Encoding

▶️ Running the Applications
✨ 1. Smart-Sync-QuickHire (Resume Matcher + Dashboard)
bash
Copy
Edit
cd "C:\Users\Admin\Downloads\autorag (7)\autorag"
streamlit run myapps.py
Upload multiple CVs and a JD.

Match candidates, analyze skill gaps, book interviews, send notifications, and view insights!

✨ 2. Candidate Course Recommender (Skill Gap → Course Recommendations)
bash
Copy
Edit
cd C:\Users\Admin\Downloads\
streamlit run myapps2.py
Upload candidate CSV (Candidate, Missing Skills columns).

Get personalized course recommendations.

Download individual candidate PDFs or all as a ZIP file.

