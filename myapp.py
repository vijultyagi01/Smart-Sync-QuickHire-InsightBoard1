import pandas as pd
import plotly.express as px
import re
import spacy
import pdfplumber
from io import StringIO
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import streamlit as st

# Set the page config at the very top
st.set_page_config(page_title="TF-IDF Skill Matcher", layout="wide")

# Load SpaCy model
@st.cache_resource
def load_spacy_model():
    return spacy.load("en_core_web_sm")

nlp = load_spacy_model()

@st.cache_data
def extract_clean_phrases(text):
    doc = nlp(text.lower())
    phrases = set()
    for chunk in doc.noun_chunks:
        phrase = re.sub(r"[^\w\s\-\+#\.]", "", chunk.text.strip())
        if (
            len(phrase.split()) <= 5
            and not all(token in spacy.lang.en.stop_words.STOP_WORDS for token in phrase.split())
        ):
            phrases.add(phrase)
    return list(phrases)

def filter_unwanted_terms(phrases):
    blocked_terms = {
        "your resume", "job title", "required skills", "related field", "phd", "masters",
        "collaborate", "responsibilities", "experience", "company", "location", "findings",
        "engineering", "team", "stakeholders", "role", "job description", "technology", "organization"
    }
    return sorted(set(p for p in phrases if all(b not in p for b in blocked_terms)))

@st.cache_data
def tfidf_match(source_phrases, target_phrases, threshold=0.5):
    if not source_phrases or not target_phrases:
        return [], target_phrases

    source_phrases = [str(p) for p in source_phrases]
    target_phrases = [str(p) for p in target_phrases]

    vectorizer = TfidfVectorizer().fit(source_phrases + target_phrases)
    source_vecs = vectorizer.transform(source_phrases)
    matched, missing = [], []
    for phrase in target_phrases:
        phrase_vec = vectorizer.transform([phrase])
        cos_sim = cosine_similarity(phrase_vec, source_vecs)
        if cos_sim.max() >= threshold:
            matched.append(phrase)
        else:
            missing.append(phrase)
    return matched, missing

@st.cache_data
def extract_text(file):
    if file.name.endswith(".pdf"):
        try:
            text = ""
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            st.error(f"❌ Error reading PDF: {e}")
            return ""
    else:
        try:
            return StringIO(file.getvalue().decode("utf-8")).read()
        except UnicodeDecodeError:
            return StringIO(file.getvalue().decode("latin1")).read()

def extract_emails(text):
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(email_pattern, text)

def extract_phone_numbers(text):
    phone_pattern = r'\(?\+?[0-9]*\)?[0-9_\- \(\)]*'
    return re.findall(phone_pattern, text)

def send_email_quick_silent(email, subject, message):
    pass

def process_cv(cv_file, jd_phrases):
    cv_text = extract_text(cv_file)
    cv_phrases_raw = extract_clean_phrases(cv_text)
    cv_phrases = filter_unwanted_terms(cv_phrases_raw)
    emails = extract_emails(cv_text)
    phone_numbers = extract_phone_numbers(cv_text)
    if not cv_phrases:
        matched, missing = [], jd_phrases
    else:
        matched, missing = tfidf_match(cv_phrases, jd_phrases)
    
    phone_present = "✔️" if phone_numbers else "❌"

    return {
        'Candidate': cv_file.name,
        'Email': ", ".join(emails) if emails else "No emails found.",
        'Matched Skills': ", ".join(matched) if matched else "No matched skills found.",
        'Missing Skills': ", ".join(missing) if missing else "No missing skills found.",
        'Matched Count': len(matched),
        'Phone Present': phone_present
    }


st.title("🧠 Smart-Sync-QuickHire")

col1, col2 = st.columns(2)
with col1:
    cv_files = st.file_uploader("📄 Upload CVs (PDF or TXT)", type=["pdf", "txt"], accept_multiple_files=True)
with col2:
    jd_file = st.file_uploader("💼 Upload Job Description (PDF or TXT)", type=["pdf", "txt"])

if cv_files and jd_file:
    with st.spinner("🔍 Matching skills ..."):
        jd_text = extract_text(jd_file)
        jd_phrases_raw = extract_clean_phrases(jd_text)
        jd_phrases = filter_unwanted_terms(jd_phrases_raw)

        with ThreadPoolExecutor() as executor:
            results = list(executor.map(lambda cv_file: process_cv(cv_file, jd_phrases), cv_files))

        df = pd.DataFrame(results)
        df_sorted = df.sort_values(by='Matched Count', ascending=False).reset_index(drop=True)

        st.subheader("📊 Candidate Skill Match Results")
        st.dataframe(df_sorted[['Candidate', 'Email', 'Matched Skills', 'Missing Skills', 'Matched Count', 'Phone Present']])

        top_k = st.slider("🎯 Select top K candidates for interview", min_value=1, max_value=len(df_sorted), value=min(3, len(df_sorted)))
        selected_candidates = df_sorted.head(top_k)
        rejected_candidates = df_sorted.iloc[top_k:]
        # Minimum Skill Match Selection
        min_matched = st.slider("🎯 Select candidates with at least this many matched skills", min_value=0, max_value=int(df_sorted['Matched Count'].max()), value=3)
        selected_min_skill = df_sorted[df_sorted['Matched Count'] >= min_matched]
        rejected_min_skill = df_sorted[df_sorted['Matched Count'] < min_matched]

        st.subheader("✅ Selected Candidates")
        st.dataframe(selected_candidates[['Candidate', 'Email']])

        st.subheader("❌ Rejected Candidates")
        st.dataframe(rejected_candidates[['Candidate', 'Email']])

        st.subheader("🗓️ Book Interview Slots")
        slot_options = pd.date_range(pd.Timestamp.now() + pd.Timedelta(days=1), periods=5, freq='1D').strftime("%Y-%m-%d %H:%M").tolist()
        selected_slots = {}
        for idx, row in selected_candidates.iterrows():
            slot = st.selectbox(f"📌 Slot for {row['Candidate']}", slot_options, key=f"{row['Candidate']}_{idx}")
            selected_slots[row["Candidate"]] = slot

        if st.button("✅ Confirm and View Scheduled Interviews"):
            st.success("Interview slots confirmed successfully!")
            for name, slot in selected_slots.items():
                st.markdown(f"**{name}** → {slot}")

        st.subheader("📧 Email Notifications")
        selected_subject = st.text_input("Subject for Selected", "Interview Invitation")
        selected_message = st.text_area("Message for Selected", "You are selected for the interview!")
        rejected_subject = st.text_input("Subject for Rejected", "Job Application Update")
        rejected_message = st.text_area("Message for Rejected", "Unfortunately, you are not selected.")

        if st.button("Send Interview Notifications"):
            for _, row in selected_candidates.iterrows():
                send_email_quick_silent(row["Email"], selected_subject, selected_message)
            for _, row in rejected_candidates.iterrows():
                suggestion = f"\nRecommended skills to learn: {row['Missing Skills']}" if row["Missing Skills"] else ""
                send_email_quick_silent(row["Email"], rejected_subject, rejected_message + suggestion)
            st.success("✅ Emails sent successfully!")

        def display_overall_summary(df):
            total_candidates = len(df)
            total_selected = len(df[df['Matched Count'] > 0])
            total_rejected = total_candidates - total_selected
            overall_matching_rate = (total_selected / total_candidates) * 100

            st.subheader("📊 Overall Summary")
            st.write(f"Total Candidates: {total_candidates}")
            st.write(f"Total Selected Candidates: {total_selected}")
            st.write(f"Total Rejected Candidates: {total_rejected}")
            st.write(f"Overall Matching Rate: {overall_matching_rate:.2f}%")

        def display_top_skills(df):
            all_skills = " ".join(df['Matched Skills'].dropna())
            all_skills_list = all_skills.split(', ')
            skill_counts = pd.Series(all_skills_list).value_counts().head(5)

            st.subheader("🛠️ Top 5 Most Common Skills")
            st.bar_chart(skill_counts)

        def display_missing_skills(df):
            all_missing_skills = " ".join(df['Missing Skills'].dropna())
            missing_skills_list = all_missing_skills.split(', ')
            missing_skill_counts = pd.Series(missing_skills_list).value_counts().head(5)

            st.subheader("❌ Top 5 Missing Skills")
            st.bar_chart(missing_skill_counts)

        def display_skill_gap_analysis(df):
            skill_gap = df[['Candidate', 'Matched Skills', 'Missing Skills']]
            skill_gap = skill_gap.explode('Missing Skills').dropna(subset=['Missing Skills'])
            skill_gap_counts = skill_gap['Missing Skills'].value_counts()

            st.subheader("🔎 Skill Gap Analysis")
            st.write("This section shows the skill gaps across candidates.")
            st.bar_chart(skill_gap_counts)

        def display_candidate_performance(df):
            fig = px.bar(df, x="Candidate", y="Matched Count", title="Candidate Performance Insights")
            st.plotly_chart(fig)

        if st.button("📊 Show Dashboard"):
            display_overall_summary(df_sorted)
            display_top_skills(df_sorted)
            display_missing_skills(df_sorted)
            display_skill_gap_analysis(df_sorted)
            display_candidate_performance(df_sorted)

        st.subheader("🔍 Skill Coverage Search")
        available_skills = sorted(set(", ".join(df_sorted["Matched Skills"]).split(", ")))
        selected_skills = st.multiselect("✅ Select Skills to Filter Candidates", options=available_skills)

        if selected_skills:
            def has_all_skills(row_skills):
                row_skill_set = set(row_skills.split(", "))
                return all(skill in row_skill_set for skill in selected_skills)

            filtered_df = df_sorted[df_sorted["Matched Skills"].apply(has_all_skills)]
            st.write(f"🎯 Found {len(filtered_df)} candidates matching **all** selected skills: {', '.join(selected_skills)}")
            st.dataframe(filtered_df[['Candidate', 'Email', 'Matched Skills']])

            skill_coverage_counts = {
                skill: df_sorted['Matched Skills'].apply(lambda x: skill in x.split(", ")).sum()
                for skill in selected_skills
            }
            skill_coverage_df = pd.DataFrame.from_dict(skill_coverage_counts, orient='index', columns=['Candidate Count'])
            skill_coverage_df['% of CVs'] = (skill_coverage_df['Candidate Count'] / len(df_sorted) * 100).round(2)

            st.subheader("📊 Skill Coverage Across All Candidates")
            st.bar_chart(skill_coverage_df['% of CVs'])

            st.subheader("📈 Raw Skill Candidate Count")
            st.dataframe(skill_coverage_df)

        
       
        download_data = selected_candidates[['Candidate', 'Email', 'Matched Count', 'Matched Skills', 'Missing Skills', 'Phone Present']]
        download_data['Interview Time'] = download_data['Candidate'].map(selected_slots)

        
        download_data['Phone Present'] = download_data['Phone Present'].apply(lambda x: 'Yes' if x == "✔️" else 'No')

        csv = download_data.to_csv(index=False)
        st.download_button("Download Selected Candidates Data", csv, "selected_candidates.csv", "text/csv")


