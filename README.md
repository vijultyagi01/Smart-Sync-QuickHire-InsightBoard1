# ⚙️ Smart-Sync-QuickHire + Skill Gap Course Recommender Suite  
## 🔍 AI-Powered Resume–JD Matcher & Dynamic Skill Gap Filler  

> **“Sync Talent. Fill Gaps. Hire Smarter. Faster. Better.”**

---

## 🚀 Project Overview

The **Smart-Sync-QuickHire + Skill Gap Course Recommender Suite** is a complete AI-powered hiring platform designed to:

- 📄 Match multiple candidate CVs against Job Descriptions (JDs)
- 🧩 Identify candidate skill gaps intelligently
- 🎯 Recommend personalized online courses to bridge missing skills
- 📑 Generate professional, candidate-specific PDF reports
- 📊 Provide recruiters with interactive dashboards for real-time insights

Built using **Streamlit** — sleek, fast, and 100% local (no cloud dependencies or paid APIs)!

---

## 💡 Key Features

- ✅ Multi-CV to JD Skill Matching  
- ✅ TF-IDF and NLP-Based Skill Extraction  
- ✅ Skill Gap Detection and Reporting  
- ✅ Personalized Course Recommendations  
- ✅ Candidate-Specific PDF Report Generation (with Clickable Course Links)  
- ✅ Bulk Download All Reports as a ZIP File  
- ✅ Interactive Recruiter Dashboards  
- ✅ Interview Slot Booking System  
- ✅ Email Notification System (Mocked)  
- ✅ Full Local Processing — No Paid APIs Needed  

---

## 📊 Dashboard Insights

| Section | Description |
|:--------|:------------|
| 📌 **Summary Metrics** | Total CVs processed, matched skills, and final candidate rankings |
| 📉 **Top Missing Skills** | Most common missing skills across candidates |
| 📈 **Candidate Performance** | Visualized matched skill counts per candidate |
| ❌ **Skill Gap Analysis** | Frequently missing skills across all CVs |
| 🧠 **Smart Skill Search** | Filter candidates by selected skills |
| 📦 **Download Hub** | Download individual or all candidate reports |

---

## 🛠️ Tech Stack

- **Language:** Python 3.8+
- **Frontend Framework:** Streamlit
- **NLP:** spaCy, TF-IDF
- **Visualization:** Plotly, pandas
- **File Parsing:** pdfplumber
- **PDF Report Generation:** FPDF
- **Concurrency:** ThreadPoolExecutor
- **Secure File Downloads:** Base64 Encoding

---

## ▶️ Running the Applications

### ✨ 1. Smart-Sync-QuickHire (Resume Matcher + Dashboard)

```bash
cd "C:\Users\Admin\Downloads\autorag (7)\autorag"
streamlit run myapps.py
