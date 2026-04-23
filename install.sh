#!/bin/bash
# Kronos Trading CLI - Quick Install Script

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Installing Kronos Trading CLI                               ║"
echo "╚══════════════════════════════════════════════════════════════╝"

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv
echo "✓ Virtual environment created"

# Activate
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies (this may take a minute)..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Make kronos executable
chmod +x kronos

# Initialize
echo ""
echo "Initializing Kronos..."
echo "paper" | ./kronos init 2>/dev/null || true

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  ✅ Installation Complete!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Quick test:"
echo "  ./kronos status"
echo ""
echo "Create a strategy:"
echo "  ./kronos strategy create my_strategy --template=mean_reversion"
echo ""
echo "Run backtest:"
echo "  ./kronos backtest my_strategy"
echo ""
echo "Start interactive mode:"
echo "  ./kronos repl"
echo ""
echo "═══════════════════════════════════════════════════════════════"
