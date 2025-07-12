#!/bin/bash

# 🚀 VPS Deployment Error Fix Script
# This script addresses the common deployment issues identified

echo "🚀 Starting VPS Deployment Error Fix..."
echo "=========================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should not be run as root for security reasons"
   exit 1
fi

# Function to print colored output
print_status() {
    echo -e "\033[1;34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[1;32m[SUCCESS]\033[0m $1"
}

print_error() {
    echo -e "\033[1;31m[ERROR]\033[0m $1"
}

print_warning() {
    echo -e "\033[1;33m[WARNING]\033[0m $1"
}

# Step 1: Check Python version
print_status "Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    print_error "Python 3 is not installed"
    exit 1
fi

# Step 2: Create virtual environment
print_status "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    if [ $? -eq 0 ]; then
        print_success "Virtual environment created"
    else
        print_error "Failed to create virtual environment"
        exit 1
    fi
else
    print_warning "Virtual environment already exists"
fi

# Step 3: Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate
if [ $? -eq 0 ]; then
    print_success "Virtual environment activated"
else
    print_error "Failed to activate virtual environment"
    exit 1
fi

# Step 4: Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Step 5: Install dependencies
print_status "Installing dependencies from requirements.txt..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        print_success "Dependencies installed successfully"
    else
        print_error "Failed to install dependencies"
        exit 1
    fi
else
    print_error "requirements.txt not found"
    exit 1
fi

# Step 6: Verify key packages are installed
print_status "Verifying critical packages..."
python -c "import binance; print('✅ python-binance installed')" 2>/dev/null || print_error "❌ python-binance not installed"
python -c "import telegram; print('✅ python-telegram-bot installed')" 2>/dev/null || print_error "❌ python-telegram-bot not installed"
python -c "import numpy; print('✅ numpy installed')" 2>/dev/null || print_error "❌ numpy not installed"
python -c "import requests; print('✅ requests installed')" 2>/dev/null || print_error "❌ requests not installed"

# Step 7: Check .env file
print_status "Checking .env configuration..."
if [ -f ".env" ]; then
    if grep -q "API_KEY=" .env && grep -q "API_SECRET=" .env; then
        API_KEY=$(grep "API_KEY=" .env | cut -d'=' -f2)
        API_SECRET=$(grep "API_SECRET=" .env | cut -d'=' -f2)
        TELEGRAM_TOKEN=$(grep "TELEGRAM_TOKEN=" .env | cut -d'=' -f2)
        TELEGRAM_CHAT_ID=$(grep "TELEGRAM_CHAT_ID=" .env | cut -d'=' -f2)
        
        if [ -z "$API_KEY" ] || [ -z "$API_SECRET" ]; then
            print_warning "API keys are empty in .env file"
            print_warning "Please edit .env file with your Binance API credentials"
        else
            print_success "API keys found in .env file"
        fi
        
        if [ -z "$TELEGRAM_TOKEN" ] || [ -z "$TELEGRAM_CHAT_ID" ]; then
            print_warning "Telegram configuration is empty in .env file"
            print_warning "Please edit .env file with your Telegram bot credentials"
        else
            print_success "Telegram configuration found in .env file"
        fi
    else
        print_error ".env file is missing required fields"
    fi
else
    print_error ".env file not found"
fi

# Step 8: Test network connectivity
print_status "Testing network connectivity..."
if curl -s --max-time 5 https://api.binance.com/api/v3/ping > /dev/null; then
    print_success "Binance API connectivity OK"
else
    print_error "Cannot reach Binance API"
fi

if curl -s --max-time 5 https://api.telegram.org > /dev/null; then
    print_success "Telegram API connectivity OK"
else
    print_error "Cannot reach Telegram API"
fi

# Step 9: Check system resources
print_status "Checking system resources..."
echo "Memory usage:"
free -h
echo ""
echo "Disk usage:"
df -h /
echo ""

# Step 10: Create a test run script
print_status "Creating test run script..."
cat > test_bot.sh << 'EOF'
#!/bin/bash
# Activate virtual environment and run bot
source venv/bin/activate
echo "🤖 Testing bot startup..."
python main.py
EOF

chmod +x test_bot.sh
print_success "Test script created: test_bot.sh"

# Step 11: Create systemd service template
print_status "Creating systemd service template..."
cat > trading-bot.service << EOF
[Unit]
Description=Trading Bot Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PWD
Environment=PATH=$PWD/venv/bin
ExecStart=$PWD/venv/bin/python $PWD/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

print_success "Service file template created: trading-bot.service"

# Final summary
echo ""
echo "=========================================="
echo "🎯 DEPLOYMENT FIX SUMMARY"
echo "=========================================="
print_success "✅ Virtual environment created and activated"
print_success "✅ Dependencies installed"
print_success "✅ Network connectivity tested"
print_success "✅ System resources checked"
print_success "✅ Service template created"

echo ""
echo "🔧 NEXT STEPS:"
echo "1. Edit .env file with your API credentials"
echo "2. Run: ./test_bot.sh to test the bot"
echo "3. If successful, install service: sudo cp trading-bot.service /etc/systemd/system/"
echo "4. Enable service: sudo systemctl enable trading-bot.service"
echo "5. Start service: sudo systemctl start trading-bot.service"
echo ""
echo "📋 IMPORTANT:"
echo "- Make sure your Binance API keys have Futures trading permissions"
echo "- Add your VPS IP to API key restrictions for security"
echo "- Test with small amounts first"
echo ""
echo "🆘 If issues persist, check: vps_deployment_fix.md"
echo "=========================================="