@echo off
cd /d %~dp0

:: Activate the virtual environment
call venv\Scripts\activate

:: Ensure spaCy model is downloaded
python -m spacy download en_core_web_sm

:: Launch the Streamlit app
streamlit run project.py

pause