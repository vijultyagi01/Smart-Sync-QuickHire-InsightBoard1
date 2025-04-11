
@echo off
cd /d %~dp0

:: Check if venv exists
IF NOT EXIST "venv\Scripts\activate.bat" (
    echo Virtual environment not found! Please create it first.
    pause
    exit /b
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Auto-download spaCy model if missing
python -m spacy download en_core_web_sm

:: Launch the Streamlit app
streamlit run project.py

pause
