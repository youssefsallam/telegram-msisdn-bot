@echo off
REM Telegram MSISDN Bot - Windows Run Script

echo.
echo 🚀 Starting Telegram MSISDN Extraction Bot...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements if needed
echo 📥 Checking requirements...
pip install -q -r requirements.txt

REM Run tests
echo.
echo ✅ Running tests...
python test_bot.py
echo.

REM Start bot
echo 🤖 Starting bot...
echo.
python main.py

pause
