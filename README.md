# ⚙️ Smart-Sync-QuickHire-InsightBoard

> 🔍 AI-Powered Resume–Job Matcher with Dynamic Skill Analysis, Candidate Ranking & Interactive Dashboards  
> _“Sync Talent. Rank Smart. Hire Faster.”_

---

## 🚀 Project Overview

**Smart-Sync-QuickHire-InsightBoard** is an advanced AI-driven platform that intelligently matches multiple CVs to multiple job descriptions (JDs), ranks candidates, identifies skill gaps, and presents interactive dashboards for recruiters – all in a sleek Streamlit web app.

---

## 💡 Key Features

✅ **Multi-CV vs Multi-JD Matching**  
✅ **BERT + TF-IDF Matching Engine**  
✅ **Skill Proficiency Estimation (Beginner to Advanced)**  
✅ **Feature Detection (LinkedIn, GitHub, Experience, etc.)**  
✅ **Customizable Weight Sliders for Ranking Logic**  
✅ **Interactive Data Dashboard (InsightBoard)**  
✅ **Email Notification to Selected & Rejected**  
✅ **Interview Slot Booking Panel**  
✅ **Zero Paid APIs – Fully Local + Free**  

---

## 📊 InsightBoard Dashboard

| Section                     | Description                                          |
|----------------------- ---  |------------------------------------------------------- 
| 📌 Summary Metrics         | Total CVs processed, Average Match & Final Scores     |
| 📉 Top Missing Skills      | Bar chart of frequently missing JD skills             |
| 📈 Final Score Histogram   | Distribution of candidate final scores                |
| 🧩 Feature Presence Charts | Visuals for LinkedIn, GitHub, Experience presence     |
| ☁️ Skill Word Cloud        | Most common extracted skills across resumes           |
| ❌ Skill Gap Frequency     | Skill demand vs supply comparison                     |

---

## 🛠️ Tech Stack

- **Language:** Python
- **Frontend:** Streamlit
- **NLP & ML:** spaCy, Sentence-BERT, TF-IDF
- **Visualization:** Plotly, Seaborn, Matplotlib, WordCloud
- **Parsing:** PyPDF2
- **Email:** SMTP (Gmail)

---

🔧 Setup Instructions



     1.Install dependencies:
                pip install -r requirements.txt
     2.Run the app:
             streamlit run project.py
     3.Optional:
             If all_skills.txt is not in the project folder, make sure to place it there or it will be auto-copied from your Downloads folder (if found).

    a. cd Smart-Sync-QuickHire-InsightBoard1
    b. streamlit run project.py

      # cd C:\Users\Admin\Desktop\SmartHireApp
      # pip install -r requirements.txt
      # streamlit run project.py


      2.
      cd "C:\Users\Admin\Downloads\autorag (7)\autorag"
      streamlit run myapps.py
      








