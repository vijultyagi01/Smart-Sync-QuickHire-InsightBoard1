import streamlit as st
import pandas as pd
import re
import smtplib
import torch
import os
import matplotlib.pyplot as plt
import spacy
from email.mime.text import MIMEText
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer, util
from wordcloud import WordCloud
import plotly.express as px

st.set_page_config(page_title="CV Matching System", page_icon="📁", layout="wide")

bert_model = SentenceTransformer('all-MiniLM-L6-v2')
nlp = spacy.load("en_core_web_sm")

@st.cache_data
def load_skills():
    with open("all_skills.txt", "r", encoding="utf-8") as f:
        return set(line.strip().lower() for line in f if len(line.strip()) > 1)

skill_set = load_skills()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    return "\n".join(page.extract_text() for page in reader.pages if page.extract_text()).strip()

def extract_skills_with_proficiency(text, known_skills):
    doc = nlp(text.lower())
    found_skills = {}
    for chunk in doc.noun_chunks:
        phrase = chunk.text.strip().lower()
        if phrase in known_skills:
            found_skills[phrase] = estimate_proficiency(phrase, text)
    return found_skills

def estimate_proficiency(skill, text):
    context = text.lower()
    if f"expert in {skill}" in context or f"advanced {skill}" in context:
        return "⭐⭐⭐ Advanced"
    elif f"intermediate {skill}" in context or f"proficient in {skill}" in context:
        return "⭐⭐ Intermediate"
    elif f"familiar with {skill}" in context or f"basic {skill}" in context:
        return "⭐ Beginner"
    return "Unknown"

def detect_features(text):
    text = text.lower()
    linkedin_pattern = re.search(r"linkedin\\.com/in/[\\w\\d-]+", text)
    github_pattern = re.search(r"github\\.com/[\\w\\d-]+", text)
    email_pattern = re.search(r"\\b[\\w\\.-]+@[\\w\\.-]+\\.\\w{2,4}\\b", text)
    phone_pattern = re.search(r"(\\+?\\d[\\d\\s().-]{8,}\\d)", text)
    portfolio_pattern = re.search(r"https?://[^\"\\s]+", text)
    experience_keywords = ["experience", "work experience", "internship", "employment history", "professional experience", "roles and responsibilities", "career timeline"]
    has_experience = any(keyword in text for keyword in experience_keywords)
    return {
        "LinkedIn": "✅" if linkedin_pattern else "❌",
        "GitHub": "✅" if github_pattern else "❌",
        "Email": "✅" if email_pattern else "❌",
        "Phone": "✅" if phone_pattern else "❌",
        "Portfolio": "✅" if portfolio_pattern else "❌",
        "Experience": "✅" if has_experience else "❌"
    }

def calculate_match_score(cv_text, job_desc):
    try:
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([cv_text, job_desc])
        tfidf_score = (tfidf_matrix[0] @ tfidf_matrix[1].T).toarray()[0][0]
    except:
        tfidf_score = 0.0
    embeddings = bert_model.encode([cv_text, job_desc], convert_to_tensor=True)
    bert_score = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()
    return round(((tfidf_score + bert_score) / 2) * 100, 2)

def send_email(recipient, subject, body):
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("Email not sent. Set credentials in environment variables.")
        return
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, recipient, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")

def skill_gap_penalty(missing_skills):
    return len(missing_skills) * 2.5

st.sidebar.title("📂 CV Matching System")
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1053/1053244.png", use_column_width=True)

st.header("📄 Upload Job Description")
jd_file = st.file_uploader("Upload Job Description (PDF)", type=["pdf"], key="jd")
jd_text = extract_text_from_pdf(jd_file) if jd_file else ""
jd_skills_map = extract_skills_with_proficiency(jd_text, skill_set) if jd_file else {}
jd_skills = list(jd_skills_map.keys())
st.text_area("Extracted Job Description", jd_text, height=200)

st.header("📂 Upload CVs")
uploaded_cvs = st.file_uploader("Upload CVs (PDF)", type=["pdf"], accept_multiple_files=True)
cv_data = []

st.sidebar.subheader("🎯 Ranking Weight Tuning")
match_weight = st.sidebar.slider("🔢 Match Score Weight", 0.0, 1.0, 0.5)
common_weight = st.sidebar.slider("🔗 Common Skills Weight", 0.0, 1.0, 0.3)
proficiency_weight = st.sidebar.slider("🌟 Proficiency Weight", 0.0, 1.0, 0.2)

def custom_score(match_score, common_skills, proficiencies):
    prof_score = sum(
        1 if p.startswith("⭐⭐⭐") else 0.5 if p.startswith("⭐⭐") else 0.2
        for p in proficiencies.values()
    ) / max(len(proficiencies), 1)
    return (match_score * match_weight) + (len(common_skills) * common_weight) + (prof_score * proficiency_weight * 100)

if uploaded_cvs and jd_text:
    feature_rows = []
    for cv_file in uploaded_cvs:
        cv_text = extract_text_from_pdf(cv_file)
        cv_skills_map = extract_skills_with_proficiency(cv_text, skill_set)
        cv_skills = list(cv_skills_map.keys())
        match_score = calculate_match_score(cv_text, jd_text)
        common_skills = sorted(set(cv_skills) & set(jd_skills))
        missing_skills = sorted(set(jd_skills) - set(cv_skills))
        rank_score = custom_score(match_score, common_skills, {k: v for k, v in cv_skills_map.items() if k in common_skills})
        penalty = skill_gap_penalty(missing_skills)
        final_score = max(match_score - penalty, 0)

        cv_data.append({
            "Candidate": cv_file.name,
            "Match Score": match_score,
            "Rank Score": round(rank_score, 2),
            "Penalty Score": penalty,
            "Final Score": round(final_score, 2),
            "Skills": ", ".join(f"{k.title()} ({v})" for k, v in cv_skills_map.items()),
            "Common Skills": ", ".join(common_skills),
            "Missing Skills": ", ".join(missing_skills),
            "Email": "candidate_email@example.com"
        })

        features = detect_features(cv_text)
        features["Candidate"] = cv_file.name
        feature_rows.append(features)

    df = pd.DataFrame(cv_data).sort_values(by="Rank Score", ascending=False)

    st.session_state["cv_data"] = cv_data
    st.session_state["feature_data"] = feature_rows

    st.subheader("📊 Matching Overview")
    col1, col2 = st.columns(2)
    col1.metric("Total CVs", len(df))
    col2.metric("Top Rank Score", df["Rank Score"].max())

    st.subheader("🏆 Ranked CVs")
    st.dataframe(df.style.format({
        "Match Score": "{:.2f}%", "Rank Score": "{:.2f}", "Penalty Score": "{:.1f}", "Final Score": "{:.2f}%"
    }).bar(subset=["Match Score", "Rank Score", "Final Score"], color='lightgreen'))

    top_k = st.slider("Select top K candidates for interview", 1, len(df), 3)
    selected_candidates = df.head(top_k)
    rejected_candidates = df.iloc[top_k:]

    if st.button("📊 Show Graph"):
        fig, ax = plt.subplots()
        ax.bar(df["Candidate"], df["Final Score"], color='skyblue')
        ax.set_xlabel("Candidates")
        ax.set_ylabel("Final Score")
        ax.set_title("Candidate Final Scores")
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)

    st.sidebar.subheader("🔍 Filter Candidates")
    min_score = st.sidebar.slider("Minimum Match Score", 0, 100, 50)
    filtered_df = df[df["Match Score"] >= min_score]
    st.sidebar.dataframe(filtered_df.style.format({"Match Score": "{:.2f}%"}))

    st.subheader("Selected Candidates")
    st.dataframe(selected_candidates.style.format({"Match Score": "{:.2f}%", "Rank Score": "{:.2f}", "Final Score": "{:.2f}%"}))

    st.subheader("🗓️ Book Interview Slots")
    slot_options = pd.date_range(pd.Timestamp.now() + pd.Timedelta(days=1), periods=5, freq='1D').strftime("%Y-%m-%d %H:%M").tolist()
    selected_slots = {}
    for _, row in selected_candidates.iterrows():
        slot = st.selectbox(f"📌 Slot for {row['Candidate']}", slot_options, key=row['Candidate'])
        selected_slots[row['Candidate']] = slot

    if st.button("✅ Confirm and View Scheduled Interviews"):
        st.success("Interview slots confirmed!")
        for name, slot in selected_slots.items():
            st.markdown(f"**{name}** → {slot}")

    st.subheader("📧 Email Notifications")
    selected_subject = st.text_input("Subject for Selected", "Interview Invitation")
    selected_message = st.text_area("Message for Selected", "You are selected for the interview!")
    rejected_subject = st.text_input("Subject for Rejected", "Job Application Update")
    rejected_message = st.text_area("Message for Rejected", "Unfortunately, you are not selected.")

    if st.button("Send Interview Notifications"):
        for _, row in selected_candidates.iterrows():
            send_email(row["Email"], selected_subject, selected_message)
        for _, row in rejected_candidates.iterrows():
            suggestion = f"\nRecommended skills to learn: {row['Missing Skills']}" if row["Missing Skills"] else ""
            send_email(row["Email"], rejected_subject, rejected_message + suggestion)
        st.success("✅ Emails sent successfully!")

    st.subheader("📄 Feature Presence Table")
    st.dataframe(pd.DataFrame(feature_rows))

if st.button("📊 Show Summary Dashboard"):
    st.subheader("📌 Overview Stats")
    total_cvs = len(st.session_state.get("cv_data", []))
    if total_cvs == 0:
        st.warning("No CVs processed yet.")
    else:
        df = pd.DataFrame(st.session_state["cv_data"])
        avg_match = df["Match Score"].mean()
        avg_final = df["Final Score"].mean()
        st.metric("Total CVs Processed", total_cvs)
        st.metric("Average Match Score", f"{avg_match:.2f}%")
        st.metric("Average Final Score", f"{avg_final:.2f}%")

        all_missing = ",".join(df["Missing Skills"].tolist()).split(",")
        top_missing = pd.Series(all_missing).value_counts().head(5)
        st.bar_chart(top_missing)

        st.subheader("📈 Final Score Distribution")
        fig1, ax1 = plt.subplots()
        ax1.hist(df["Final Score"], bins=10, color='skyblue', edgecolor='black')
        ax1.set_title("Distribution of Final Scores")
        ax1.set_xlabel("Final Score")
        ax1.set_ylabel("Number of Candidates")
        st.pyplot(fig1)

        st.subheader("🔍 Feature Presence Breakdown")
        feature_df = pd.DataFrame(st.session_state.get("feature_data", []))
        for feature in ["LinkedIn", "GitHub", "Experience"]:
            pie_df = feature_df[feature].value_counts()
            fig = px.pie(names=pie_df.index, values=pie_df.values, title=f"{feature} Presence")
            st.plotly_chart(fig)

        st.subheader("🔤 Common Skills Word Cloud")
        all_skills = ",".join(df["Skills"].tolist()).lower()
        wc = WordCloud(width=800, height=400, background_color='white').generate(all_skills)
        fig_wc, ax_wc = plt.subplots()
        ax_wc.imshow(wc, interpolation='bilinear')
        ax_wc.axis("off")
        st.pyplot(fig_wc)

        st.subheader("❌ Skill Gap Frequency")
        gap_skills = pd.Series(",".join(df["Missing Skills"].tolist()).split(",")).value_counts()
        st.bar_chart(gap_skills.head(10))
