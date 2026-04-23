# 🌙 Kronos Trading CLI

> **Autonomous Trading Agent with RL + Kronos Oracle**

A professional, OpenCode-inspired CLI for backtesting trading strategies, creating new strategies from templates, and running autonomous paper/live trading with built-in risk management.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

```
╔══════════════════════════════════════════════════════════════╗
║  ██╗  ██╗██████╗  ██████╗ ███╗   ██╗ ██████╗ ███████╗         ║
║  ██║ ██╔╝██╔══██╗██╔═══██╗████╗  ██║██╔═══██╗██╔════╝         ║
║  █████╔╝ ██████╔╝██║   ██║██╔██╗ ██║██║   ██║███████╗         ║
║  ██╔═██╗ ██╔══██╗██║   ██║██║╚██╗██║██║   ██║╚════██║         ║
║  ██║  ██╗██║  ██║╚██████╔╝██║ ╚████║╚██████╔╝███████║         ║
║  ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝         ║
╠══════════════════════════════════════════════════════════════╣
║      Autonomous Trading Agent with RL + Kronos Oracle         ║
╚══════════════════════════════════════════════════════════════╝
```

## ✨ Features

- 🎯 **Strategy Management** - Create, edit, and organize trading strategies from templates
- 📊 **Backtest Engine** - Full historical backtesting with performance metrics
- 🤖 **Autonomous Trading** - Paper and live trading modes with risk controls
- 🖥️ **Beautiful CLI** - Rich colors, tables, and progress spinners
- ⚡ **Interactive REPL** - Hands-on strategy development
- 🛡️ **Risk Management** - Built-in daily loss limits, max drawdown stops
- 🔧 **Configuration** - Persistent user settings

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/charan9832/kronos-trading-cli.git
cd kronos-trading-cli

# Install dependencies
pip install -r requirements.txt

# Or install as a package
pip install -e .

# Initialize Kronos (first-time setup)
./kronos init

# Create a strategy
./kronos strategy create my_strategy --template=momentum

# Run backtest
./kronos backtest my_strategy --symbol=SPY

# Start paper trading
./kronos run --mode=paper --strategy=my_strategy

# Interactive mode
./kronos repl
```

## 📋 Commands

### Initialize
```bash
./kronos init
```
Sets up configuration directory (`~/.kronos`) and guides you through initial setup.

### Strategy Management
```bash
./kronos strategy list                     # List all strategies
./kronos strategy create <name>             # Create from template
./kronos strategy create <name> --template=momentum|mean_reversion|breakout|rl_kronos
./kronos strategy edit <name>              # Edit in your default editor
```

### Backtest
```bash
./kronos backtest <strategy> [options]
  --symbol    Trading symbol (default: SPY)
  --start     Start date (default: 2020-01-01)
  --end       End date (default: 2024-12-31)
  --capital   Initial capital (default: 100000)
```

Example:
```bash
./kronos backtest momentum --symbol=AAPL --start=2022-01-01 --end=2023-12-31 --capital=50000
```

### Run Trading
```bash
./kronos run --mode=paper --strategy=momentum    # Paper trading
./kronos run --mode=live --strategy=momentum     # ⚠️ Real money
```

### Status & Config
```bash
./kronos status                              # Show current status
./kronos config                              # View configuration
./kronos config --set auto_trade=true        # Update setting
```

### Interactive REPL
```bash
./kronos repl
```

REPL commands:
- `strategies` - List strategies
- `create <name>` - Create strategy
- `backtest <strategy>` - Run backtest
- `run [strategy] [mode]` - Start trading
- `stop` - Stop trading bot
- `status` - Show status
- `exit` - Quit REPL

## 🏗️ Architecture

```
Kronos Trading Agent
├── Strategies (Python modules)
│   ├── momentum.py          - Trend following
│   ├── mean_reversion.py     - Buy low, sell high
│   ├── breakout.py           - Price breakouts
│   └── rl_kronos.py          - RL-enhanced oracle
├── Backtest Engine
│   ├── Historical simulation
│   ├── Performance metrics
│   └── Report generation
├── Trading Bot
│   ├── Paper trading mode
│   ├── Live trading mode
│   └── Risk management
└── Configuration
    ├── Risk limits
    ├── API credentials
    └── Trading preferences
```

## 📊 Built-in Strategy Templates

| Template | Description | Type |
|----------|-------------|------|
| `momentum` | Trend-following using rolling returns | Trend |
| `mean_reversion` | Buy when below MA, sell when above | Reversion |
| `breakout` | Trade price breakouts above/below ranges | Breakout |
| `rl_kronos` | RL agent wrapping Kronos predictions | AI/ML |

## 📈 Backtest Output

```
╭─────────────────┬──────────────────────────╮
│ Metric          │ Value                    │
├─────────────────┼──────────────────────────┤
│ Period          │ 2023-01-01 to 2023-12-31 │
│ Symbol          │ SPY                      │
│ Initial Capital │ $100,000.00              │
│ Final Equity    │ $114,420.00              │
│ Total Return    │ +14.42%                  │
│ Sharpe Ratio    │ 1.47                     │
│ Max Drawdown    │ 4.65%                    │
│ Win Rate        │ 54.2%                    │
│ Num Trades      │ 32                       │
╰─────────────────┴──────────────────────────╯
```

## 🛡️ Risk Management

Built-in safety limits:
- **Daily Loss Limit** (default: 2%) - Stop trading after daily loss
- **Max Drawdown** (default: 10%) - Hard stop on portfolio drawdown
- **Max Position Size** (default: 100%) - Limit per-position exposure
- **Max Trades/Day** (default: 10) - Prevent overtrading

## 📝 Creating Custom Strategies

Strategies are Python files with a `generate_signals` function:

```python
import pandas as pd
import numpy as np

def generate_signals(prices: pd.Series) -> pd.Series:
    """
    Generate trading signals.
    
    Returns position sizes (-1.0 to 1.0):
    -1.0 = Full short
     0.0 = No position
     1.0 = Full long
    """
    # Example: Moving average crossover
    fast_ma = prices.rolling(20).mean()
    slow_ma = prices.rolling(50).mean()
    
    signals = pd.Series(0.0, index=prices.index)
    signals[fast_ma > slow_ma] = 1.0   # Long
    signals[fast_ma < slow_ma] = -1.0  # Short
    
    return signals
```

## ⚙️ Configuration

Configuration stored in `~/.kronos/config.json`:

```json
{
  "api_key": "",
  "api_secret": "",
  "default_mode": "paper",
  "risk_daily_loss_pct": 2.0,
  "risk_max_drawdown_pct": 10.0,
  "risk_max_position_size": 1.0,
  "auto_trade": false,
  "notification_email": ""
}
```

## 🧪 Example Workflow

```bash
# 1. Initialize
./kronos init

# 2. Create and test momentum strategy
./kronos strategy create momentum --template=momentum
./kronos backtest momentum --symbol=SPY

# 3. Compare with mean reversion
./kronos strategy create meanrev --template=mean_reversion
./kronos backtest meanrev --symbol=SPY

# 4. Pick best strategy
./kronos status

# 5. Run paper trading
./kronos run --mode=paper --strategy=meanrev

# 6. Use interactive mode for exploration
./kronos repl
```

## 📦 Installation as Package

```bash
# Clone repository
git clone https://github.com/charan9832/kronos-trading-cli.git
cd kronos-trading-cli

# Install in editable mode
pip install -e .

# Now you can use 'kronos' command anywhere
kronos init
kronos status
```

## 🔮 Future Enhancements

- [ ] Live broker integration (Alpaca, Interactive Brokers)
- [ ] Real-time market data feeds (OpenBB, yfinance)
- [ ] Web dashboard for monitoring
- [ ] Strategy optimization with Optuna
- [ ] Multi-asset portfolio support
- [ ] ML model training pipeline
- [ ] Telegram/Discord notifications
- [ ] Docker containerization

## 🐛 Troubleshooting

**Strategy not found:**
```bash
./kronos strategy list  # Check available strategies
```

**Backtest fails:**
- Check strategy syntax: `./kronos strategy edit <name>`
- Ensure `generate_signals` function exists and returns `pd.Series`

**Missing dependencies:**
```bash
pip install -r requirements.txt
```

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📜 License

MIT License - See [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

Built with:
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal output
- [PyTorch](https://pytorch.org/) - Deep learning framework
- [Pandas](https://pandas.pydata.org/) - Data manipulation

---

**Built with ❤️ by Charan**

```
```
