#!/bin/bash

# PAS Bot Setup Script

echo "========================================="
echo "PAS Bot - Initial Setup"
echo "========================================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.10+ is required. Current version: $python_version"
    exit 1
fi

echo "✓ Python version: $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "✓ Virtual environment created"

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✓ Dependencies installed"

# Download spaCy models
echo "Downloading language models..."
python -m spacy download ru_core_news_sm

echo "✓ Language models downloaded"

# Create .env file if not exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created - Please edit it with your API keys"
else
    echo "✓ .env file already exists"
fi

# Create necessary directories
echo "Creating data directories..."
mkdir -p data/logs
mkdir -p data/rag
mkdir -p data/templates

echo "✓ Directories created"

# Check PostgreSQL
if command -v psql &> /dev/null; then
    echo "✓ PostgreSQL is installed"
    echo "Note: Don't forget to create the database: createdb pas_bot"
else
    echo "⚠ PostgreSQL not found. Please install it for production use."
fi

# Check Redis
if command -v redis-cli &> /dev/null; then
    echo "✓ Redis is installed"
else
    echo "⚠ Redis not found. Please install it for production use."
fi

echo ""
echo "========================================="
echo "Setup complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Create PostgreSQL database: createdb pas_bot"
echo "3. Run migrations: alembic upgrade head"
echo "4. Start the bot: python main.py"
echo ""
echo "For more information, see README.md"