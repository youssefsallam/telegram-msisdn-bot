#!/bin/bash
# Telegram MSISDN Bot - Run Script

echo "🚀 Starting Telegram MSISDN Extraction Bot..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements if needed
if ! python -c "import telegram" 2>/dev/null; then
    echo "📥 Installing requirements..."
    pip install -q -r requirements.txt
fi

# Run tests
echo ""
echo "✅ Running tests..."
python test_bot.py
echo ""

# Start bot
echo "🤖 Starting bot..."
echo ""
python main.py
