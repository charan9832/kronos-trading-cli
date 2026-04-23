# Kronos Trading CLI

A professional, OpenCode-inspired CLI for autonomous trading with reinforcement learning and the Kronos prediction oracle.

## 🚀 Quick Start

```bash
# Initialize Kronos (first-time setup)
./kronos init

# Create a trading strategy
./kronos strategy create my_strategy --template=momentum

# Run backtest
./kronos backtest my_strategy --symbol=SPY --start=2023-01-01 --end=2023-12-31

# Start paper trading
./kronos run --mode=paper --strategy=my_strategy

# Interactive REPL mode
./kronos repl
```

## 📋 Commands

### `kronos init`
Initialize the trading environment and configuration.
- Sets up configuration directory (`~/.kronos`)
- Configures risk parameters
- Sets default trading mode (paper/live)

### `kronos strategy`
Manage trading strategies.

**Subcommands:**
- `list` - List all available strategies
- `create <name>` - Create a new strategy from template
- `edit <name>` - Edit a strategy in your default editor

**Templates:**
- `momentum` - Trend-following momentum strategy
- `mean_reversion` - Buy low, sell high mean reversion
- `breakout` - Price breakout strategy
- `rl_kronos` - RL-enhanced with Kronos oracle

**Example:**
```bash
./kronos strategy create momentum_trader --template=momentum
./kronos strategy list
./kronos strategy edit momentum_trader
```

### `kronos backtest`
Run backtests on strategies with visual results.

**Options:**
- `strategy` (required) - Strategy name
- `--symbol` - Trading symbol (default: SPY)
- `--start` - Start date (default: 2020-01-01)
- `--end` - End date (default: 2024-12-31)
- `--capital` - Initial capital (default: 100000)

**Example:**
```bash
./kronos backtest momentum_trader --symbol=AAPL --start=2022-01-01 --end=2023-12-31 --capital=50000
```

**Output Metrics:**
- Total Return (%)
- Sharpe Ratio
- Max Drawdown (%)
- Win Rate (%)
- Number of Trades

### `kronos run`
Start autonomous trading.

**Options:**
- `--mode` - Trading mode: `paper` or `live`
- `--strategy` - Strategy to use

**Example:**
```bash
./kronos run --mode=paper --strategy=momentum_trader
./kronos run --mode=live --strategy=rl_kronos  # ⚠️ Real money
```

### `kronos status`
Show current system status including:
- Configuration
- Available strategies
- Recent backtest results

### `kronos config`
View and edit configuration.

**Options:**
- `--set key=value` - Set a configuration value

**Example:**
```bash
./kronos config
./kronos config --set auto_trade=true
./kronos config --set risk_daily_loss_pct=1.5
```

### `kronos repl`
Start interactive REPL mode for hands-on trading.

**REPL Commands:**
- `help` - Show available commands
- `strategies` - List strategies
- `create <name> [template]` - Create strategy
- `backtest <strategy>` - Run backtest
- `run [strategy] [mode]` - Start trading
- `stop` - Stop trading bot
- `status` - Show status
- `config` - Show configuration
- `clear` - Clear screen
- `exit` / `quit` - Exit REPL

## 🏗️ Architecture

```
Kronos Trading Agent
├── Strategies (custom Python modules)
│   ├── momentum.py
│   ├── mean_reversion.py
│   ├── breakout.py
│   └── rl_kronos.py
├── Backtest Engine
│   ├── Historical data simulation
│   ├── Signal generation
│   ├── Performance metrics
│   └── Report generation
├── Trading Bot
│   ├── Paper trading mode
│   ├── Live trading mode (future)
│   ├── Risk management
│   └── Autonomous execution
└── Configuration
    ├── Risk limits
    ├── API credentials
    └── Trading preferences
```

## 📝 Creating Custom Strategies

Strategies are Python modules with a `generate_signals` function:

```python
import pandas as pd
import numpy as np

def generate_signals(prices: pd.Series) -> pd.Series:
    """
    Generate trading signals.
    
    Args:
        prices: Price series
        
    Returns:
        Series of position sizes (-1.0 to 1.0)
        -1.0 = Full short
         0.0 = No position
         1.0 = Full long
    """
    # Your strategy logic here
    signals = pd.Series(0.0, index=prices.index)
    
    # Example: Simple moving average crossover
    fast_ma = prices.rolling(20).mean()
    slow_ma = prices.rolling(50).mean()
    
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

## 🔒 Risk Management

Built-in risk limits:
- **Daily Loss Limit** (default: 2%) - Stop trading after daily loss
- **Max Drawdown** (default: 10%) - Hard stop on portfolio drawdown
- **Max Position Size** (default: 100%) - Limit per-position exposure
- **Max Trades/Day** (default: 10) - Prevent overtrading

## 📊 Backtest Reports

Backtest results saved to `/tmp/kronos_project/results/`:
- JSON format with full metrics
- Equity curve data
- Trade-by-trade returns

## 🛠️ Installation

```bash
# Clone or copy the project
cd /tmp/kronos_project

# Make executable
chmod +x kronos

# Create symlink (optional)
ln -sf /tmp/kronos_project/kronos /usr/local/bin/kronos

# Install dependencies
pip install rich numpy pandas torch

# Initialize
./kronos init
```

## 🔄 Workflow Example

```bash
# 1. Initialize
./kronos init

# 2. Create momentum strategy
./kronos strategy create momentum --template=momentum

# 3. Backtest it
./kronos backtest momentum --symbol=SPY

# 4. Create mean reversion for comparison
./kronos strategy create meanrev --template=mean_reversion
./kronos backtest meanrev --symbol=SPY

# 5. Pick best strategy and paper trade
./kronos run --mode=paper --strategy=meanrev

# 6. Check status anytime
./kronos status
```

## 🧪 Interactive Mode

The REPL mode is great for experimentation:

```bash
./kronos repl
```

```
kronos> strategies
  • momentum
  • meanrev
kronos> backtest momentum
[shows backtest results]
kronos> run momentum paper
[starts trading bot]
kronos> stop
[stops bot]
kronos> exit
```

## 🚧 Future Enhancements

- [ ] Live broker integration (Alpaca, Interactive Brokers)
- [ ] Real-time market data feeds
- [ ] Web dashboard
- [ ] Strategy optimization with Optuna
- [ ] Multi-asset portfolios
- [ ] ML model training pipeline
- [ ] Telegram/Discord notifications

## 🐛 Troubleshooting

**Strategy not found:**
```bash
./kronos strategy list  # Check available strategies
```

**Backtest fails:**
- Check strategy syntax: `./kronos strategy edit <name>`
- Ensure `generate_signals` function exists

**Missing dependencies:**
```bash
pip install rich numpy pandas torch
```

## 📜 License

MIT License - See LICENSE file for details

---

**Built with ❤️ using Python + Rich + PyTorch**
