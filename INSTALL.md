# Kronos Trading CLI - Installation Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (to clone the repo)

## Quick Install (Recommended)

### Option 1: Clone and Run Directly

```bash
# 1. Clone the repository
git clone https://github.com/charan9832/kronos-trading-cli.git
cd kronos-trading-cli

# 2. Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run Kronos
./kronos init
```

### Option 2: Install as System Package

```bash
# Clone and install
git clone https://github.com/charan9832/kronos-trading-cli.git
cd kronos-trading-cli
pip install -e .

# Now 'kronos' command works anywhere
kronos init
kronos status
```

## Step-by-Step Verification

After installation, verify everything works:

```bash
# Test 1: Check help works
./kronos --help

# Test 2: Initialize (creates ~/.kronos/)
./kronos init
# Enter: paper, 2.0, 10.0, n

# Test 3: Create a strategy
./kronos strategy create test_strategy --template=mean_reversion

# Test 4: List strategies
./kronos strategy list

# Test 5: Run backtest
./kronos backtest test_strategy --symbol=SPY --start=2023-01-01 --end=2023-12-31

# Test 6: Check status
./kronos status

# Test 7: View config
./kronos config

# Test 8: Interactive mode (type 'exit' to quit)
./kronos repl
```

## What Gets Installed

```
~/.kronos/                      # Config directory
├── config.json                 # Your settings
└── strategies/                 # Strategy files
    ├── test_strategy.py
    └── ...

/tmp/kronos_project/ or your chosen dir
├── kronos                      # Main CLI
├── code/                       # Core modules
├── models/                     # Saved RL models
├── results/                    # Backtest reports
└── logs/                       # Trading logs
```

## Troubleshooting

### Issue: "command not found: kronos"
**Fix:** Use `./kronos` (with ./) or install with `pip install -e .`

### Issue: "No module named 'rich'"
**Fix:** Run `pip install -r requirements.txt`

### Issue: Permission denied
**Fix:** Run `chmod +x kronos`

### Issue: Python version too old
**Fix:** Ensure Python 3.8+ with `python3 --version`

### Issue: Backtest fails with import error
**Fix:** Make sure you're in the virtual environment:
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows
```

## macOS Specific

```bash
# Install Python if needed
brew install python3

# Then follow Quick Install steps above
```

## Windows Specific

```powershell
# In PowerShell or CMD
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python kronos init
```

## Docker Alternative (Future)

```bash
# If you prefer Docker (not yet implemented)
docker build -t kronos .
docker run -it kronos
```

## Next Steps After Install

1. **Create strategies:**
   ```bash
   ./kronos strategy create momentum --template=momentum
   ./kronos strategy create meanrev --template=mean_reversion
   ```

2. **Backtest them:**
   ```bash
   ./kronos backtest momentum --symbol=AAPL
   ./kronos backtest meanrev --symbol=MSFT
   ```

3. **Compare results** and pick the best

4. **Run paper trading:**
   ```bash
   ./kronos run --mode=paper --strategy=meanrev
   ```

## Live Trading Setup (Advanced)

To enable live trading, you'll need:
- Broker API keys (Alpaca, Interactive Brokers, etc.)
- Add keys to config: `./kronos config --set api_key=YOUR_KEY`

⚠️ **WARNING:** Only use live mode with money you can afford to lose!

## Uninstall

```bash
# If installed with pip -e
pip uninstall kronos-trading

# Remove config
rm -rf ~/.kronos

# Remove repo
cd ..
rm -rf kronos-trading-cli
```

## Need Help?

Run any command with issues? The CLI will show helpful error messages.

Common debug command:
```bash
./kronos status  # Shows everything about your setup
```
