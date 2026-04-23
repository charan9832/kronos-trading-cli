# Kronos AI Trading Agent

> **trade CLI + Kronos AI Model = Conversational Autonomous Trading**

```
╔══════════════════════════════════════════════════════════════╗
║  █████████╗██████╗  █████╗ ██████╗ ███████╗                   ║
║  ╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗██╔════╝                   ║
║     ██║   ██████╔╝███████║██║  ██║█████╗                     ║
║     ██║   ██╔══██╗██╔══██║██║  ██║██╔══╝                     ║
║     ██║   ██║  ██║██║  ██║██████╔╝███████╗                   ║
║     ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚══════╝                   ║
╠══════════════════════════════════════════════════════════════╣
║  CLI Interface for the Kronos AI Trading Model                 ║
╚══════════════════════════════════════════════════════════════╝
```

## 🎯 What is This?

**Two components working together:**

1. **`trade`** - The CLI command tool (this repo)  
   - Interface to interact with the Kronos AI
   - Manages strategies, backtests, trading

2. **Kronos** - The AI model itself  
   - Multimodal trading intelligence
   - **Native conversational ability** (built into the model)
   - Understands markets, explains decisions, answers questions

Think of it like: `trade` = your terminal, `Kronos` = the AI brain

---

## ✨ Features

### Kronos AI Model
- 🧠 **Native Conversational** - Talk to Kronos about trading naturally
- 📊 **Multimodal** - Price data + news + charts + conversation
- 🔮 **Decision Explanation** - Kronos explains WHY it trades
- 🎓 **Trading Knowledge** - Built-in understanding of strategies, risk, markets

### trade CLI
- 🎯 **Strategy Management** - Create, edit, organize strategies
- 📈 **Backtest Engine** - Historical testing with metrics
- 🤖 **Autonomous Trading** - Paper and live modes
- 🖥️ **Beautiful Interface** - Rich colors, tables, spinners
- 🛡️ **Risk Controls** - Daily loss limits, max drawdown stops

---

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/charan9832/kronos-trading-cli.git
cd kronos-trading-cli

# Install dependencies
pip install -r requirements.txt

# Initialize - THIS INSTALLS THE KRONOS AI MODEL
./trade init

# Talk to Kronos AI
./trade chat
```

### During `trade init`, you'll choose:
- **Local mode** - Download Kronos model weights (~2GB)
- **Cloud mode** - Use Azure OpenAI (language) + cloud inference
- **Hybrid mode** - Local trading logic + cloud language

---

## 💬 Talking to Kronos

```bash
$ ./trade chat

╦╔═┌─┐┌─┐┌─┐┌┐┌
╠╩╗│ ││ ││ ││││
╩ ╩└─┘└─┘└─┘┘└┘

Kronos AI Model - Native Conversational Trading Agent
Type your message or 'help' for examples. 'exit' to quit.

You: What do you think about Tesla's momentum?
Kronos: TSLA is showing strong upward momentum with RSI at 72 and 
volume 40% above average. The breakout above $250 resistance suggests 
continued bullish sentiment. However, be cautious as it's approaching 
overbought territory. My momentum model suggests HOLD for now - wait 
for a pullback or confirmation above $260.

You: Should I diversify more?
Kronos: Your current portfolio is 60% tech (AAPL, NVDA, MSFT). That's 
concentrated risk. Consider adding exposure to healthcare (XLV) or 
utilities (XLU) to reduce correlation. A 70/30 tech/defensive split 
would reduce your portfolio beta from 1.3 to around 1.0.

You: Explain why you sold yesterday
Kronos: I sold AAPL at $185.50 because:
1. Hit our trailing stop (10% from peak)
2. MACD showed bearish crossover
3. Overall market VIX spiked to 25
The exit preserved our 12% gain rather than risking reversal.
```

---

## 📋 Commands

### Core Commands
```bash
./trade init              # Install Kronos AI model & setup
./trade chat              # Talk to Kronos AI naturally
./trade repl              # Interactive command mode
```

### Strategy Management
```bash
./trade strategy list                          # List strategies
./trade strategy create <name>                 # Create from template
./trade strategy create <name> --template=momentum|mean_reversion|breakout|rl_kronos
./trade strategy edit <name>                   # Edit in your $EDITOR
```

### Backtest & Trade
```bash
./trade backtest <strategy> [options]
  --symbol    Trading symbol (default: SPY)
  --start     Start date (default: 2020-01-01)
  --end       End date (default: 2024-12-31)
  --capital   Initial capital (default: 100000)

./trade run --mode=paper --strategy=<name>     # Paper trading
./trade run --mode=live --strategy=<name>      # ⚠️ Real money
```

### Status & Config
```bash
./trade status            # Show system status
./trade config            # View/edit configuration
```

---

## 🧠 Kronos AI Model Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    KRONOS AI MODEL                        │
├─────────────────────────────────────────────────────────┤
│  Inputs                      │  Outputs                 │
│  ─────────────────────────   │  ────────────────────    │
│  • Price history (OHLCV)     │  • Trading actions       │
│  • News text                 │  • Q-value estimates     │
│  • Chart images (vision)     │  • Natural language!     │
│  • Market state              │  (explanations, chat)    │
│  • User questions            │                          │
├─────────────────────────────────────────────────────────┤
│              Multimodal Fusion Transformer                │
├─────────────────────────────────────────────────────────┤
│  [Trading Policy Head]  [Q-Value Head]  [Language Head]│
│       ↓                        ↓              ↓          │
│    BUY/SELL/HOLD          Value estimate   Explanations │
│                                            Chat replies  │
└─────────────────────────────────────────────────────────┘
```

**Three Modes:**
- **TRADE** - Silent autonomous trading
- **CHAT** - Conversational Q&A
- **HYBRID** - Trade AND explain every decision

---

## 🎓 How It Works

1. **You talk naturally** - "Should I buy Tesla?"
2. **Kronos understands** - Uses its native language capability (NOT command parsing)
3. **Kronos responds** - Market analysis + recommendation + reasoning
4. **Can execute** - "Yes, execute that trade" → Kronos trades

The conversation ability is **built INTO the Kronos model itself**, not a wrapper script.

---

## ⚙️ Configuration

Config stored in `~/.kronos/config.json`:

```json
{
  "default_mode": "paper",
  "risk_daily_loss_pct": 2.0,
  "risk_max_drawdown_pct": 10.0,
  "auto_trade": false,
  "model_mode": "hybrid",
  "azure_endpoint": "...",
  "azure_key": "..."
}
```

---

## 📁 Directory Structure

```
~/.kronos/
├── config.json          # Your configuration
├── strategies/          # Trading strategies
│   ├── momentum.py
│   ├── mean_reversion.py
│   └── your_strategy.py
└── models/              # Kronos AI model
    └── kronos-v1/
        ├── config.json
        └── weights.bin  # Downloaded during init
```

---

## 🛠️ Development

```bash
# Run tests
pytest tests/

# Development mode
pip install -e .

# Type checking
mypy code/
```

---

## 🤝 Contributing

This is an OpenCode-inspired project. Key principles:

1. **Small, composable modules** (`code/` directory)
2. **Agent-first** - Easy for AI agents to work with
3. **Self-contained** - All logic in one codebase
4. **Clear naming** - `trade` CLI, `Kronos` AI model

---

## 📜 License

MIT License - See LICENSE file

---

## 🙏 Acknowledgments

- Inspired by [OpenCode](https://github.com/sst/opencode) architecture
- Kronos model uses PyTorch + Transformers
- CLI built with [Rich](https://github.com/Textualize/rich)

---

**Questions?** Just ask Kronos: `./trade chat` 🤖📈
