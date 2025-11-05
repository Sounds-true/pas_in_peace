#!/bin/bash

# PAS Bot - Mac Setup Script
# Автоматическая установка и настройка на macOS

set -e  # Exit on error

echo "╔════════════════════════════════════════╗"
echo "║   PAS Bot - Mac Setup Script          ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check PostgreSQL and Redis
echo -e "${YELLOW}[1/9]${NC} Checking PostgreSQL and Redis..."
if brew services list | grep -q "postgresql@15.*started"; then
    echo -e "${GREEN}✓${NC} PostgreSQL is running"
else
    echo -e "${YELLOW}→${NC} Starting PostgreSQL..."
    brew services start postgresql@15
    sleep 3
fi

if brew services list | grep -q "redis.*started"; then
    echo -e "${GREEN}✓${NC} Redis is running"
else
    echo -e "${YELLOW}→${NC} Starting Redis..."
    brew services start redis
    sleep 2
fi

# Step 2: Create virtual environment
echo -e "${YELLOW}[2/9]${NC} Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${GREEN}✓${NC} Virtual environment already exists"
fi

# Step 3: Activate venv and install dependencies
echo -e "${YELLOW}[3/9]${NC} Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo -e "${GREEN}✓${NC} Dependencies installed"

# Step 4: Download spaCy models
echo -e "${YELLOW}[4/9]${NC} Downloading spaCy language models..."
python -m spacy download ru_core_news_sm --quiet
echo -e "${GREEN}✓${NC} Language models downloaded"

# Step 5: Configure .env
echo -e "${YELLOW}[5/9]${NC} Configuring environment variables..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${YELLOW}!${NC} .env file created - YOU NEED TO EDIT IT!"
    echo -e "   Add your Telegram and OpenAI keys:"
    echo -e "   ${YELLOW}nano .env${NC}"
else
    echo -e "${GREEN}✓${NC} .env file exists"
fi

# Step 6: Create database
echo -e "${YELLOW}[6/9]${NC} Creating pas_bot database..."
if createdb pas_bot 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Database created"
else
    echo -e "${GREEN}✓${NC} Database already exists"
fi

# Step 7: Run migrations
echo -e "${YELLOW}[7/9]${NC} Running database migrations..."
alembic upgrade head
echo -e "${GREEN}✓${NC} Migrations complete"

# Step 8: Verify installation
echo -e "${YELLOW}[8/9]${NC} Verifying installation..."
echo -e "${GREEN}✓${NC} PostgreSQL: $(psql --version | head -1)"
echo -e "${GREEN}✓${NC} Redis: $(redis-cli --version)"
echo -e "${GREEN}✓${NC} Python: $(python --version)"

# Step 9: Ready!
echo ""
echo "╔════════════════════════════════════════╗"
echo "║   Setup Complete! 🎉                  ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "1. Edit .env file:"
echo "   ${YELLOW}nano .env${NC}"
echo ""
echo "2. Add your API keys:"
echo "   - TELEGRAM_BOT_TOKEN (get from @BotFather)"
echo "   - OPENAI_API_KEY (get from OpenAI)"
echo ""
echo "3. Start the bot:"
echo "   ${YELLOW}source venv/bin/activate${NC}"
echo "   ${YELLOW}python main.py${NC}"
echo ""
echo "4. Test in Telegram:"
echo "   Send /start to your bot"
echo ""
echo "Happy coding! 🚀"
