import os
import pandas as pd
import logging
import zipfile
from io import BytesIO
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fpdf import FPDF
import streamlit as st
import base64

# Setup
logging.basicConfig(level=logging.INFO)
st.set_page_config(page_title="Candidate Course Recommender", page_icon="🚀", layout="centered")
st.title("🚀 Candidate-Course Recommender")
st.markdown("Find the best online courses to fill missing skills for each candidate. 📚")

# Load course data (fixed, hardcoded)
courses_df = pd.read_csv(r"C:\Users\Admin\Downloads\autorag (7)\autorag\Online_Courses.csv")

# Upload button for candidate CSV
uploaded_candidate_file = st.file_uploader("📄 Upload Candidate CSV (with missing skills)", type=["csv"])

if uploaded_candidate_file is not None:
    candidates_df = pd.read_csv(uploaded_candidate_file)
    st.success("✅ Candidate dataset uploaded successfully!")

    # Process only if file uploaded

    # Extract missing skills
    missing_skills_per_candidate = {}
    for _, row in candidates_df.iterrows():
        candidate_id = row['Candidate']
        raw = row['Missing Skills']
        if pd.notnull(raw):
            skills = [s.strip() for s in str(raw).split(',') if s.strip()]
            if skills:
                missing_skills_per_candidate[candidate_id] = skills

    # Preprocess courses
    filtered_courses_df = courses_df.dropna(subset=['Course Title', 'Course URL']).reset_index(drop=True)
    filtered_courses_df['full_text'] = (
        filtered_courses_df['Course Title'].fillna('') + ' ' +
        filtered_courses_df['Course Short Intro'].fillna('')
    )

    # TF-IDF Vectorization
    course_texts = filtered_courses_df['full_text'].tolist()
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    course_tfidf_matrix = tfidf_vectorizer.fit_transform(course_texts)

    # Match skill to top courses
    def find_top_courses_for_skill(skill_name, top_n=1):
        skill_vec = tfidf_vectorizer.transform([skill_name])
        sims = cosine_similarity(skill_vec, course_tfidf_matrix).flatten()
        top_indices = sims.argsort()[-top_n:][::-1]
        return filtered_courses_df.iloc[top_indices][['Course Title', 'Course URL']]

    # PDF generator
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 14)
            self.cell(0, 10, 'Recommended Courses', ln=True, align='C')
            self.ln(10)

        def course_table(self, records):
            self.set_font('Arial', 'B', 10)
            self.cell(50, 10, 'Skill', border=1, align='C')
            self.cell(80, 10, 'Course Title', border=1, align='C')
            self.cell(60, 10, 'Link', border=1, align='C')
            self.ln()
            self.set_font('Arial', '', 9)
            for skill, title, url in records:
                self.cell(50, 10, skill[:20], border=1)
                self.cell(80, 10, title[:35], border=1)
                self.set_text_color(0, 0, 255)
                self.cell(60, 10, 'Click Here', border=1, link=url)
                self.set_text_color(0, 0, 0)
                self.ln()

    def generate_pdf(candidate_name, records):
        if not os.path.exists("pdf_reports"):
            os.makedirs("pdf_reports")
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.course_table(records)
        filename = f"pdf_reports/{candidate_name[:25].replace('/', '-')}_recommendation.pdf"
        pdf.output(filename)
        return os.path.abspath(filename)

    # Build skill-to-course mapping
    unique_skills = set(skill for skills in missing_skills_per_candidate.values() for skill in skills)
    skill_to_courses = {}
    for skill in unique_skills:
        courses = find_top_courses_for_skill(skill)
        skill_to_courses[skill] = courses if not courses.empty else None

    # Build summary data for Streamlit display
    final_summary_data = []

    for candidate, skills in missing_skills_per_candidate.items():
        matched, unmatched = 0, 0
        seen_courses = set()
        records_for_pdf = []

        for skill in skills:
            added_course_for_skill = False
            if skill_to_courses.get(skill) is not None:
                for _, row in skill_to_courses[skill].iterrows():
                    course_key = (row['Course Title'].strip(), row['Course URL'].strip())
                    if course_key not in seen_courses:
                        records_for_pdf.append((skill, row['Course Title'], row['Course URL']))
                        seen_courses.add(course_key)
                        added_course_for_skill = True
                        break
            if not added_course_for_skill:
                unmatched += 1
            else:
                matched += 1

        # Generate PDF for the candidate
        pdf_path = generate_pdf(candidate, records_for_pdf)

        final_summary_data.append({
            "Candidate Name": candidate,
            "Missing Skills Count": len(skills),
            "Recommended Courses Count": matched,
            "PDF Path": pdf_path
        })

    # Prepare table data
    table_rows = []
    for row in final_summary_data:
        candidate_name = row["Candidate Name"]
        missing_skills_count = row["Missing Skills Count"]
        recommended_courses_count = row["Recommended Courses Count"]
        pdf_path = row["PDF Path"]

        try:
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            b64 = base64.b64encode(pdf_bytes).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(pdf_path)}">📄 Download PDF</a>'
        except Exception:
            href = "❌ Error"

        table_rows.append([candidate_name, missing_skills_count, recommended_courses_count, href])

    # Create nice dataframe
    df_display = pd.DataFrame(table_rows, columns=["Candidate Name", "Missing Skills Count", "Recommended Courses Count", "Download PDF"])

    # Show the table beautifully
    with st.container():
        st.markdown("### 📄 Final Summary Table")
        st.write(df_display.to_html(escape=False, index=False), unsafe_allow_html=True)

    # Optional: Offer Download All PDFs as ZIP
    if st.button("📦 Download All PDFs as Zip"):
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for row in final_summary_data:
                pdf_path = row["PDF Path"]
                zip_file.write(pdf_path, arcname=os.path.basename(pdf_path))
        zip_buffer.seek(0)
        st.download_button(label="Download Zip 📥", data=zip_buffer, file_name="all_pdfs.zip", mime="application/zip")

else:
    st.warning("⚠️ Please upload a Candidate CSV file to proceed.")

