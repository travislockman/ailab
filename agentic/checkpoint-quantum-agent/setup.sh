#!/bin/bash

# Check Point Quantum Blue Team Agent - Setup Script
echo "🛡️  Setting up Check Point Quantum Blue Team Agent..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.11+ is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create environment file
if [ ! -f .env ]; then
    echo "📝 Creating environment file..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your Check Point and OpenAI credentials"
else
    echo "✅ Environment file already exists"
fi

# Create logs directory
mkdir -p logs

echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your credentials"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python -m src.main --health"
echo "4. Run: python -m src.main --interactive"

