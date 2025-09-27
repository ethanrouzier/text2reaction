#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Setting up Text2Reaction project..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python -m venv .venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Copy environment file
echo "⚙️ Setting up environment..."
cp .env.example .env

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your MISTRAL_API_KEY"
echo "2. Run: source .venv/bin/activate"
echo "3. Run: export \$(grep -v '^#' .env | xargs)"
echo "4. Run: python -m flask --app app.main run --debug"
echo "5. Open http://127.0.0.1:5000"
echo ""
echo "Or simply run: make run"
